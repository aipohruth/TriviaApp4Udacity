import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME_TEST, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME_TEST
        self.database_path = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASSWORD, "localhost:5432", self.database_name
)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            "question": "My name?", 
            "answer": "Melissa", 
            "difficulty": 1, 
            "category": 5
            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test to retrieve categories
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["categories"])
        
        
    # test to retrieve questions
    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    # test to retreve questions with a wrong page parameter

    def test_retrieve_questions_404(self):
        res = self.client().get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        
     # test to  delete a question with id 16
     
    def test_delete_question(self):
        res = self.client().delete('/questions/16')
        data = json.loads(res.data)

        question = Question.query.filter_by(id=16).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],16)

    
    # test delete a questions with a id that is not in the database
    def test_delete_question_422(self):
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')


    # test to create question

    def test_create_question(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_question_creation_not_allowed(self):
        response = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


    # test to search with results

    def test_search(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'invented'})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
    #test to search not in db
    def test_search_without_results(self):
        response = self.client().post('/questions/search', json={'searchTerm':'zxt'})

        data = json.loads(response.data)

        self.assertEqual(data['total_questions'],0)
        self.assertEqual(data['success'], True)
    

    # test to get questions by category
    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['current_category'], 'Science')
        self.assertEqual(data['success'], True)
        
    # test to get questions by category not included
    def test_get_404_questions_by_category(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    # test to play quiz
    def test_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {'type': 'Art', 'id': 13}}
        response = self.client().post('/play', json=quiz_round)
        data = json.loads(response.data)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_quiz(self):
        response = self.client().post('/play')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()