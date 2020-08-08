from typing import List


def get_tokens(word: str) -> List[str]:
    """
    Creates a list of tokens for a string. This is very basic, more complex
    tokens could be created using combinations of all the words in the
    string
    """
    tokens: List[str] = [word] + word.split()

    # Lowercase and remove spaces
    tokens = [token.lower().strip() for token in tokens]
    # Make sure it's not a list of empty strings
    tokens = [token for token in tokens if tokens]

    return tokens


def get_tokens_for_tags(tags: str) -> List[str]:
    """
    Tags are usually a list of space separated words, starting with
    a hashtag. The whole list is not a token, however it's chuncks are
    """
    tags: List[str] = tags.split()

    # Lowercase, remove leading # and spaces
    tags = [tag.lstrip("#").lower().strip() for tag in tags]

    # Make sure it's not a list of empty strings
    tags = [tag for tag in tags if tag]

    return tags
