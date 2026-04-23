from app.services.mbti import derive_mbti


def test_derive_mbti_clear_enfp():
    scores = {
        "extraversion": [0.8, 0.9],
        "intuition": [0.7],
        "thinking": [0.2],
        "judging": [0.1, 0.2],
    }
    result = derive_mbti(scores)
    assert result.mbti == "ENFP"
    assert abs(result.dimensions.extraversion - 0.85) < 1e-9
    assert abs(result.dimensions.intuition - 0.7) < 1e-9
    assert abs(result.dimensions.thinking - 0.2) < 1e-9
    assert abs(result.dimensions.judging - 0.15) < 1e-9


def test_derive_mbti_missing_dimensions_default_to_half():
    # Only extraversion present. Others default to 0.5 -> first letter (N, T, J).
    result = derive_mbti({"extraversion": [0.9]})
    assert result.mbti == "ENTJ"
    assert result.dimensions.intuition == 0.5
    assert result.dimensions.thinking == 0.5
    assert result.dimensions.judging == 0.5


def test_derive_mbti_exactly_half_resolves_to_first_letter():
    scores = {
        "extraversion": [0.5],
        "intuition": [0.5],
        "thinking": [0.5],
        "judging": [0.5],
    }
    result = derive_mbti(scores)
    assert result.mbti == "ENTJ"


def test_derive_mbti_clear_isfj():
    scores = {
        "extraversion": [0.1],
        "intuition": [0.3],
        "thinking": [0.2],
        "judging": [0.8],
    }
    result = derive_mbti(scores)
    assert result.mbti == "ISFJ"


def test_derive_mbti_averages_multiple_scores_per_dimension():
    scores = {
        "extraversion": [0.2, 0.4, 0.6],  # avg = 0.4 -> I
        "intuition": [0.9],
        "thinking": [0.8],
        "judging": [0.9],
    }
    result = derive_mbti(scores)
    assert result.mbti == "INTJ"
    assert abs(result.dimensions.extraversion - 0.4) < 1e-9
