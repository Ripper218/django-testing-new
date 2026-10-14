from http import HTTPStatus


from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Хороший комментарий', }
BAD_FORM_DATA = {'text': {BAD_WORDS[0]}}


def test_anonymous_cannot_create_comment(client, news, detail_url):
    response = client.post(detail_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_author_can_create_comment(author_client, author, detail_url, news):
    response = author_client.post(detail_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    comment = Comment.objects.get()
    assert Comment.objects.count() == 1
    assert comment.news == news
    assert comment.author == author
    assert comment.text == FORM_DATA['text']


def test_comment_creation_redirects_to_comments_anchor(
    author_client, detail_url, detail_url_comments
):
    response = author_client.post(detail_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_comments
    assert Comment.objects.count() == 1


def test_bad_word_rejected(author_client, news, detail_url):
    response = author_client.post(detail_url, data=BAD_FORM_DATA)

    form = response.context['form']
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    assert form.errors['text'] == [
        WARNING
    ]


def test_author_can_edit_own_comment(
    author_client, comment, edit_url, detail_url_comments
):
    response = author_client.post(edit_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_comments

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_author_can_delete_own_comment(
    author_client, comment, delete_url, detail_url_comments,
):
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == detail_url_comments
    assert Comment.objects.count() == 0


def test_reader_cannot_edit_foreign_comment(reader_client, comment, edit_url):
    response = reader_client.post(edit_url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.NOT_FOUND

    saved = Comment.objects.get(pk=comment.pk)
    assert saved.text == comment.text
    assert saved.news == comment.news
    assert saved.author == comment.author


def test_reader_cannot_delete_foreign_comment(
    reader_client, comment, delete_url,
):
    response = reader_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    saved = Comment.objects.get(pk=comment.pk)
    assert saved.text == comment.text
    assert saved.news == comment.news
    assert saved.author == comment.author
