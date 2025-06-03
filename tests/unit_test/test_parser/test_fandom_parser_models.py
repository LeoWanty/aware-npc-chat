from datetime import datetime

from pydantic import HttpUrl

from knowledge_base.parser.fandom.models import Contributor, Text, Revision, Page, SiteInfo, FandomSiteContent


# Basic tests to ensure models can be instantiated (not for XML parsing itself)

def test_contributor():
    c1 = Contributor(username="TestUser", id=123)
    c2 = Contributor(ip="127.0.0.1")
    c3 = Contributor(id=" ")
    assert c3.id is None
    assert c1.username == "TestUser"
    assert c2.ip == "127.0.0.1"

def test_text():
    t1 = Text(content="Hello world", bytes=123, sha1="abc")
    t2 = Text(deleted=True)
    t3 = Text(bytes="")
    assert t3.bytes is None
    assert t1.content == "Hello world"
    assert t2.deleted is True

def test_revision():
    c1 = Contributor(username="TestUser", id=123)
    t1 = Text(content="Hello world", bytes=123, sha1="abc")
    rev1 = Revision(id=1, timestamp=datetime.now(), contributor=c1, comment="A test revision", text=t1, parentid=" ")
    assert rev1.parentid is None
    assert rev1.id == 1
    assert rev1.comment == "A test revision"

def test_page():
    c1 = Contributor(username="TestUser", id=123)
    t1 = Text(content="Hello world", bytes=123, sha1="abc")
    rev1 = Revision(id=1, timestamp=datetime.now(), contributor=c1, comment="A test revision", text=t1)
    p1 = Page(title="Test Page", ns=0, id=1, revisions=[rev1])
    p2 = Page(title="Redirect Page", ns=0, id=2, redirect_title="Test Page")
    assert p1.title == "Test Page"
    assert p2.redirect_title == "Test Page"

def test_siteinfo():
    http_url = HttpUrl("http://example.com/wiki")
    si1 = SiteInfo(sitename="Test Wiki", base=http_url, namespaces={0: "Articles", 1: "Talk"})
    assert si1.sitename == "Test Wiki"
    assert si1.base == HttpUrl("http://example.com/wiki")
    assert si1.namespaces[0] == "Articles"

def test_knowledge_base():
    si1 = SiteInfo(sitename="Test Wiki", base="http://example.com/wiki", namespaces={0: "Articles", 1: "Talk"})
    c1 = Contributor(username="TestUser", id=123)
    t1 = Text(content="Hello world", bytes=123, sha1="abc")
    rev1 = Revision(id=1, timestamp=datetime.now(), contributor=c1, comment="A test revision", text=t1)
    p1 = Page(title="Test Page", ns=0, id=1, revisions=[rev1])
    p2 = Page(title="Redirect Page", ns=0, id=2, redirect_title="Test Page")
    kb1 = FandomSiteContent(siteinfo=si1, pages=[p1, p2])
    assert kb1.siteinfo.sitename == "Test Wiki"
    assert len(kb1.pages) == 2
