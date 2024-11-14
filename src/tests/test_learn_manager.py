import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import timedelta, datetime
from managers.LearnManager import LearnManager
from fastapi import HTTPException
from models import *
from schemas.gembow import WordCreate, ExampleCreate

TEST_WORD_ID = 123
TEST_USER_ID = 22
TEST_USER_EMAIL = "test@email.com"
TEST_CATEGORY_NAME = "CAT"
TEST_CATEGORY_ID = 67


@pytest.mark.parametrize("number, expected", [
    (0, timedelta(hours=1)),
    (1, timedelta(hours=5)),
    (2, timedelta(days=1)),
    (3, timedelta(days=5)),
    (4, timedelta(days=20)),
    (5, timedelta(days=60)),
    (6, None),
    (-1, None),
    (123, None),

])
def test_get_interval(number, expected):
    assert LearnManager.get_interval(number) == expected


@pytest.mark.parametrize("number, delta", [
    (0, timedelta(hours=1)),
    (1, timedelta(hours=5)),
    (2, timedelta(days=1)),
    (3, timedelta(days=5)),
    (4, timedelta(days=20)),
    (5, timedelta(days=60)),
    (6, None),
    (-1, None),
    (123, None),

])
def test_get_next_repeat_time(number, delta):
    result = LearnManager.get_next_repeat_time(number)

    if delta == None:
        assert result == None
    else:

        assert result < datetime.now() + delta + timedelta(seconds=1)
        assert result > datetime.now() + delta - timedelta(seconds=1)


@pytest.mark.asyncio
async def test_start_learning_limit():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(last_learn_count=5, dayly_goal=3))):
        result = await LearnManager.start_learning(1, User(), MagicMock())
        assert isinstance(result, HTTPException)
        assert result.status_code == 429
        assert result.detail == "You have reached your dayly goal (5/3)"


@pytest.mark.asyncio
async def test_start_learning_forbidden():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(last_learn_count=3, dayly_goal=5))):

        session = MagicMock()

        session.get = AsyncMock(
            return_value=Word(id=TEST_WORD_ID, owner_id=55))

        result = await LearnManager.start_learning(TEST_WORD_ID, User(id=TEST_USER_ID, email=TEST_USER_EMAIL), session)

        assert isinstance(result, HTTPException)
        assert result.status_code == 403


@pytest.mark.asyncio
async def test_start_learning_not_found():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(last_learn_count=3, dayly_goal=5))):

        session = MagicMock()

        session.get = AsyncMock(return_value=None)

        result = await LearnManager.start_learning(TEST_WORD_ID, User(id=TEST_USER_ID, email=TEST_USER_EMAIL), session)

        assert isinstance(result, HTTPException)
        assert result.status_code == 404


@pytest.mark.asyncio
async def test_start_learning_already_learning():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(last_learn_count=3, dayly_goal=5))):

        session = MagicMock()

        async def mock_session_get(model, key):
            # Проверяем, какой передан model и key, и возвращаем разные значения
            if model == Word:
                return Word(id=TEST_WORD_ID)
            elif model == Relation_user_word:
                return Relation_user_word()

        session.get = AsyncMock(side_effect=mock_session_get)

        result = await LearnManager.start_learning(TEST_WORD_ID, User(id=TEST_USER_ID, email=TEST_USER_EMAIL), session)

        assert isinstance(result, HTTPException)
        assert result.status_code == 409


@pytest.mark.asyncio
async def test_start_learning_limit_after():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(learned_words=0, learning_words=0, known_words=0, problematic_words=0, last_learn_count=4, dayly_goal=5))):

        session = MagicMock()
        session.commit = AsyncMock()

        async def mock_session_get(model, key):
            # Проверяем, какой передан model и key, и возвращаем разные значения
            if model == Word:
                return Word(id=TEST_WORD_ID)
            elif model == Relation_user_word:
                return None

        session.get = AsyncMock(side_effect=mock_session_get)

        result = await LearnManager.start_learning(TEST_WORD_ID, User(id=TEST_USER_ID, email=TEST_USER_EMAIL), session)

        assert isinstance(result, HTTPException)
        assert result.status_code == 429


@pytest.mark.asyncio
async def test_start_learning_valid():
    with patch("managers.StatsManager.StatsManager.get_stats", new=AsyncMock(return_value=Stats(learned_words=0, learning_words=0, known_words=0, problematic_words=0, last_learn_count=3, dayly_goal=5))):

        session = MagicMock()
        session.commit = AsyncMock()

        async def mock_session_get(model, key):
            # Проверяем, какой передан model и key, и возвращаем разные значения
            if model == Word:
                return Word(id=TEST_WORD_ID)
            elif model == Relation_user_word:
                return None

        session.get = AsyncMock(side_effect=mock_session_get)

        result = await LearnManager.start_learning(TEST_WORD_ID, User(id=TEST_USER_ID, email=TEST_USER_EMAIL), session)

        assert isinstance(result, Relation_user_word)
        assert result.user_id == TEST_USER_ID
        assert result.word_id == TEST_WORD_ID


@pytest.mark.asyncio
async def test_get_words_to_repeat_no_limit():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    exec_result = MagicMock()

    return_list = [Word(id=TEST_WORD_ID), Word(id=TEST_WORD_ID+1)]

    exec_result.unique.return_value.scalars.return_value.all.return_value = return_list

    session.execute = AsyncMock(return_value=exec_result)

    result = await LearnManager.get_words_to_repeat(user, session)

    assert result == return_list


@pytest.mark.asyncio
async def test_get_words_to_repeat_time_limited():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    exec_result = MagicMock()

    return_list = [Word(id=TEST_WORD_ID)]

    exec_result.unique.return_value.scalars.return_value.all.return_value = return_list

    session.execute = AsyncMock(return_value=exec_result)

    result = await LearnManager.get_words_to_repeat(user, session, True)

    assert result == return_list


@pytest.mark.asyncio
async def test_repeat_word_not_found():
    user = User(id=TEST_USER_ID)
    session = MagicMock()
    session.get = AsyncMock(return_value=None)

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert isinstance(result, HTTPException)
    assert result.status_code == 404


@pytest.mark.asyncio
async def test_repeat_word_cant_repeat():
    user = User(id=TEST_USER_ID)
    session = MagicMock()
    session.get = AsyncMock(return_value=Relation_user_word(
        state=LearningState.ALREADY_KNOWN))

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert isinstance(result, HTTPException)
    assert result.status_code == 409


@pytest.mark.asyncio
async def test_repeat_word_not_time():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    rel = Relation_user_word(state=LearningState.LEARNING,
                             next_repeat=datetime.now() + timedelta(days=1))

    session.get = AsyncMock(return_value=rel)

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert result == rel


@pytest.mark.asyncio
async def test_repeat_word_default():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    repeat_iter = 2


    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.LEARNING,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )

    session.get = AsyncMock(return_value=rel)
    session.commit = AsyncMock()

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert isinstance(result, Relation_user_word)
    assert result.repeat_iteration - 1 == repeat_iter
    
    
@pytest.mark.asyncio
async def test_repeat_word_unproblem():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    repeat_iter = 2


    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.LEARNING_PROBLEMATIC,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )

    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None

    session.get = AsyncMock(side_effect=mock_session_get)
    session.commit = AsyncMock()

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert isinstance(result, Relation_user_word)
    assert result.state == LearningState.LEARNING



@pytest.mark.asyncio
async def test_repeat_word_learned():
    user = User(id=TEST_USER_ID)
    session = MagicMock()

    repeat_iter = 5


    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.LEARNING,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )

    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None

    session.get = AsyncMock(side_effect=mock_session_get)
    session.commit = AsyncMock()

    result = await LearnManager.repeat_word(TEST_WORD_ID, user, session)

    assert isinstance(result, Relation_user_word)
    assert result.state == LearningState.LEARNED
    
    
@pytest.mark.asyncio
async def test_forget_word():
    
    repeat_iter = 2
    
    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.LEARNING,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )
    
    
    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None
    
    session = MagicMock()
    session.commit = AsyncMock()
    
    session.get = AsyncMock(side_effect=mock_session_get)
    
    result = await LearnManager.forget_word(TEST_WORD_ID, User(id=TEST_USER_ID), session)
    
    assert isinstance(result, Relation_user_word)
    assert result.state == LearningState.LEARNING_PROBLEMATIC
    
@pytest.mark.asyncio
async def test_forget_word_not_found():

    session = MagicMock()
    session.commit = AsyncMock()
    
    session.get = AsyncMock(return_value = None)
    
    result = await LearnManager.forget_word(TEST_WORD_ID, User(id=TEST_USER_ID), session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 404
    
    
@pytest.mark.asyncio
async def test_forget_word_cannot():
    
    repeat_iter = 6
    
    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.ALREADY_KNOWN,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )
    
    
    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None
    
    session = MagicMock()
    session.commit = AsyncMock()
    
    session.get = AsyncMock(side_effect=mock_session_get)
    
    result = await LearnManager.forget_word(TEST_WORD_ID, User(id=TEST_USER_ID), session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 409
    
    
@pytest.mark.asyncio
async def test_already_known_invalid():
    
    repeat_iter = 2
    
    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.ALREADY_KNOWN,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )
    
    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None
    
    
    session = MagicMock()
    session.commit = AsyncMock()
    
    session.get = AsyncMock(side_effect=mock_session_get)
    
    
    result = await LearnManager.already_know(TEST_WORD_ID, User())
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 409
    

@pytest.mark.asyncio
async def test_already_known():
    

    
    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return None
        return None
    
    
    session = MagicMock()
    session.commit = AsyncMock(return_value = None)
    
    session.get = AsyncMock(side_effect=mock_session_get)
    
    
    result = await LearnManager.already_know(TEST_WORD_ID, User(), session)
    
    assert isinstance(result, Relation_user_word)
    
    session.commit.assert_called()
    session.add.assert_called()
    
    
    
@pytest.mark.asyncio
async def test_already_known_invalid():
    
    repeat_iter = 2
        
    rel = Relation_user_word(
        word_id = TEST_WORD_ID,
        user_id = TEST_USER_ID,
        state=LearningState.ALREADY_KNOWN,
        next_repeat=datetime.now() - timedelta(days=1),
        repeat_iteration=repeat_iter
    )
        
    async def mock_session_get(model, id):
        if model == Stats:
            return Stats(
                user_id = TEST_USER_ID,
                learned_words = 5,
                learning_words = 6,
                known_words = 7,
                problematic_words = 8
            )
        elif model == Relation_user_word:
            return rel
        return None
    
    
    session = MagicMock()
    session.commit = AsyncMock(return_value = None)
    
    session.get = AsyncMock(side_effect=mock_session_get)
    
    
    result = await LearnManager.already_know(TEST_WORD_ID, User(), session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 409
    
    
@pytest.mark.asyncio
async def test_get_earliest_next_repeat():
    
    exec_res = MagicMock()
    
    
    dt = datetime.now() + timedelta(hours=1)
    
    exec_res.scalar.return_value = dt
    session = MagicMock()
    session.execute = AsyncMock(return_value= exec_res)
    
    result = await LearnManager.get_earliest_next_repeat(TEST_USER_ID, session)
    
    assert result == dt
    
    
@pytest.mark.asyncio
async def test_create_category():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    
    result = await LearnManager.create_category(TEST_CATEGORY_NAME, User(id=TEST_USER_ID), session)
    
    assert isinstance(result, Category)
    assert result.name == TEST_CATEGORY_NAME
    assert result.owner_id == TEST_USER_ID
    session.add.assert_called_once()
    session.commit.assert_called_once()
    
    

@pytest.mark.asyncio
async def test_add_word_category_not_found():
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    
    result = await LearnManager.add_word(MagicMock(), User(), session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 404
    
@pytest.mark.asyncio
async def test_add_word_category_forbidden():
    session = MagicMock()
    session.get = AsyncMock(return_value=Category(owner_id=TEST_USER_ID + 1))
    
    result = await LearnManager.add_word(MagicMock(), User(id=TEST_USER_ID), session)
    
    assert isinstance(result, HTTPException)
    assert result.status_code == 403
    
@pytest.mark.asyncio
async def test_add_word_category():
    session = MagicMock()
    
    exec_res = MagicMock()
    example_word = Word(id = TEST_WORD_ID, categories = [Category(id=TEST_CATEGORY_ID)])
    exec_res.scalars.return_value.first.return_value = example_word
    
    session.get = AsyncMock(return_value=Category(owner_id=TEST_USER_ID))
    session.commit = AsyncMock()
    session.execute = AsyncMock(return_value=exec_res)
    
    words_scheme = WordCreate(
        category_id = TEST_CATEGORY_ID,
        english = "cat",
        russian = "кот",
        transcription="'ca:t",
        examples= [ExampleCreate(russian="black cat", english="черный кот")]
    )
    
    
    result = await LearnManager.add_word(words_scheme, User(id=TEST_USER_ID), session)
    
    assert result == example_word
    
    session.add.assert_called()
    session.commit.assert_called()
    
    
    
    