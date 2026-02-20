import re
from urllib.parse import urlparse


class LinkParser:
    """
    Parse Instagram links and extract type + username/story_id
    
    Supported formats:
    - @username
    - username
    - instagram.com/username
    - instagram.com/p/CODE
    - instagram.com/reel/CODE
    - instagram.com/username/reel/CODE
    - instagram.com/stories/username/STORY_ID

    NOT Supported (should fail):
    - instagram.com/stories/highlights/ID
    - instagram.com/s/ENCODED_STRING (highlights share link)
    """

    TYPE_USERNAME = 'username'
    TYPE_PROFILE = 'profile'
    TYPE_POST = 'post'
    TYPE_REEL = 'reel'
    TYPE_STORY = 'story'
    TYPE_HIGHLIGHT = 'highlight'  # Not supported

    @staticmethod
    def parse(link):
        """
        Parse link and return dict with type and extracted info

        Returns:
            {
                'type': str,
                'username': str or None,
                'story_id': str or None,
                'post_code': str or None,
                'original': str
            }
        """
        link = link.strip()

        result = {
            'type': None,
            'username': None,
            'story_id': None,
            'post_code': None,
            'original': link
        }

        # Check for highlights (not supported)
        if LinkParser.is_highlight_link(link):
            result['type'] = LinkParser.TYPE_HIGHLIGHT
            return result

        # Case 1: @username
        if link.startswith('@'):
            result['type'] = LinkParser.TYPE_USERNAME
            result['username'] = link[1:]
            return result

        # Case 2: Plain username (no special chars, no dots at start/end)
        if LinkParser._is_plain_username(link):
            result['type'] = LinkParser.TYPE_USERNAME
            result['username'] = link
            return result

        # Case 3: URL
        if 'instagram.com' in link:
            return LinkParser._parse_instagram_url(link, result)

        # Default: treat as username
        result['type'] = LinkParser.TYPE_USERNAME
        result['username'] = link
        return result

    @staticmethod
    def is_highlight_link(link):
        """Check if link is a highlights link (not supported)"""
        link_lower = link.lower()

        # Pattern 1: /stories/highlights/ID
        if '/stories/highlights/' in link_lower:
            return True

        # Pattern 2: /s/ENCODED (share link for highlights)
        if '/s/' in link_lower and ('highlight' in link_lower or 'story_media_id' in link_lower):
            return True

        # Pattern 3: instagram.com/s/ (generic share link - likely highlight)
        if re.search(r'instagram\.com/s/[a-zA-Z0-9]+', link):
            return True

        return False

    @staticmethod
    def _is_plain_username(text):
        """Check if text is a valid Instagram username"""
        if not text or len(text) > 30:
            return False

        if '/' in text or ':' in text or 'http' in text.lower():
            return False

        pattern = r'^[a-zA-Z0-9](?!.*\.\.)[a-zA-Z0-9_.]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        return bool(re.match(pattern, text))

    @staticmethod
    def _parse_instagram_url(link, result):
        """Parse Instagram URL"""
        parsed = urlparse(link)

        if parsed.netloc not in ['instagram.com', 'www.instagram.com']:
            result['type'] = LinkParser.TYPE_USERNAME
            result['username'] = link
            return result

        path_parts = [p for p in parsed.path.strip('/').split('/') if p]

        if not path_parts:
            return result

        # stories/highlights/ID (not supported)
        if path_parts[0] == 'stories' and len(path_parts) >= 2 and path_parts[1] == 'highlights':
            result['type'] = LinkParser.TYPE_HIGHLIGHT
            return result

        # stories/username/story_id
        if path_parts[0] == 'stories' and len(path_parts) >= 2:
            result['type'] = LinkParser.TYPE_STORY
            result['username'] = path_parts[1]
            if len(path_parts) >= 3:
                result['story_id'] = path_parts[2]
            return result

        # p/CODE (post)
        if path_parts[0] == 'p' and len(path_parts) >= 2:
            result['type'] = LinkParser.TYPE_POST
            result['post_code'] = path_parts[1]
            return result

        # reel/CODE
        if path_parts[0] == 'reel' and len(path_parts) >= 2:
            result['type'] = LinkParser.TYPE_REEL
            result['post_code'] = path_parts[1]
            return result

        # username/reel/CODE
        if len(path_parts) >= 3 and path_parts[1] == 'reel':
            result['type'] = LinkParser.TYPE_REEL
            result['username'] = path_parts[0]
            result['post_code'] = path_parts[2]
            return result

        # username/p/CODE
        if len(path_parts) >= 3 and path_parts[1] == 'p':
            result['type'] = LinkParser.TYPE_POST
            result['username'] = path_parts[0]
            result['post_code'] = path_parts[2]
            return result

        # Just username (profile URL)
        if len(path_parts) == 1:
            result['type'] = LinkParser.TYPE_PROFILE
            result['username'] = path_parts[0]
            return result

        return result

    @staticmethod
    def extract_username(link):
        """Convenience method to just get username from any link type"""
        parsed = LinkParser.parse(link)
        return parsed.get('username')

    @staticmethod
    def is_story_link(link):
        """Check if link is a direct story URL"""
        parsed = LinkParser.parse(link)
        return parsed.get('type') == LinkParser.TYPE_STORY

    @staticmethod
    def is_highlight_link_static(link):
        """Check if link is a highlight (not supported)"""
        parsed = LinkParser.parse(link)
        return parsed.get('type') == LinkParser.TYPE_HIGHLIGHT

    @staticmethod
    def is_post_or_reel(link):
        """Check if link is a post or reel URL"""
        parsed = LinkParser.parse(link)
        return parsed.get('type') in [LinkParser.TYPE_POST, LinkParser.TYPE_REEL]

    @staticmethod
    def needs_username_extraction(link):
        """Check if we need to fetch page to get username"""
        parsed = LinkParser.parse(link)
        return parsed.get('type') in [LinkParser.TYPE_POST, LinkParser.TYPE_REEL] and not parsed.get('username')