from dataclasses import dataclass

@dataclass
class Post:
    def __init__(self, post_id, timestamp, content, likes):
        self.post_id = post_id
        self.timestamp = timestamp
        self.content = content
        self.likes = likes
        self.category = None
        self.thread = None
        self.is_main= False

@dataclass
class Category:
    def __init__(self, name, description, threads, posts, url):
        self.id = None
        self.name = name
        self.description = description
        self.threads = threads
        self.posts = posts
        self.url = url

@dataclass
class Thread:
    def __init__(self, title, comments, likes, url):
        self.id = None
        self.title = title
        self.comments = comments
        self.likes = likes
        self.url = url
        self.posts = []
        self.category = None

@dataclass
class User:
    def __init__(self, url) :
        self.id = None
        self.signature = None
        self.url = url
        self.posts = []
        self.threads = []
        self.likes = []