import bs4

from aioscrapy import select_one, select_all, select_text_one


def test_select_one():
    html = bs4.BeautifulSoup(f'''
        <html>
            <body>
                <div class="foo" attr-name="attr-value">bar</div>
                <div class="foo">bar2</div>
            </body>
        </html>
    ''', 'lxml')
    assert select_one(html, '.foo', 'attr-name') == "attr-value"
    assert select_one(html, 'div', 'text') == "bar"
    assert select_one(html, '.fooerror', 'attr-name', 'default') == 'default'
    assert select_one(html, '.foo', 'attr-error', 'default') == 'default'


def test_select_text_one():
    html = bs4.BeautifulSoup(f'''
        <html>
            <body>
                <div class="foo" attr-name="attr-value">bar</div>
                <div class="foo">bar2</div>
            </body>
        </html>
    ''', 'lxml')
    assert select_text_one(html, '[attr-name="attr-value"]') == "bar"


def test_select_all():
    html = bs4.BeautifulSoup(f'''
            <html>
                <body>
                    <div class="foo" attr-name="attr-value">bar</div>
                    <div class="foo">bar2</div>
                </body>
            </html>
        ''', 'lxml')
    assert select_all(html, '.foo', 'text') == ['bar', 'bar2']
    assert select_all(html, 'div', 'attr-name') == ['attr-value']
