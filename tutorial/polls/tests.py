import datetime
from django.test import TestCase
from django.utils import timezone
from .models import Question
from django.urls import reverse


# Create your tests here.


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for question with pub_date in the future
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for question with pub_date more that 1 day older
        :return:
        """
        time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=12)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given question_text and offset of days.
    Days positive if in the future or negative if in the past
    :param question_text:
    :param days:
    :return: Question
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionDetailViewTests(TestCase):
    def test_past_question(self):
        """
        Test that a past question details is displayed
        :return:
        """
        past_question = create_question(question_text="Past question", days=-1)

        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))

        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        """
        Test thtat a past question is not displayed
        :return:
        """

        future_question = create_question(question_text="Future question", days=1)

        response = self.client.get(reverse('polls:detail',args=(future_question.id,)))

        self.assertEqual(response.status_code, 404)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no question exist, an appripiate text is displayes
        :return:
        """
        response = self.client.get(reverse('polls:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a past date are displayed
        :return:
        """
        create_question(question_text="Past question", days=-2)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_future_question(self):
        """
        Questions with a future date are not displayed
        :return:
        """
        create_question(question_text="Future question", days=2)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_two_past_questions(self):
        """
        All question in the past should be displayed
        :return:
        """
        create_question(question_text="Past question 1", days=-2)
        create_question(question_text="Past question 2", days=-5)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ["<Question: Past question 1>", "<Question: Past question 2>"])

    def test_past_and_future_questions(self):
        """
        Question in the past should display.
        Question in the future shouldn't display
        :return:
        """

        create_question(question_text="Past question", days=-1)
        create_question(question_text="Future question", days=1)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(response.context['latest_question_list'], ["<Question: Past question>"])
