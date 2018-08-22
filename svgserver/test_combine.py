from .combine import CombineSVG
from io import BytesIO

def test_simple():
	#
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-1"><path></path></g><g id="layer-2"><path></path></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))


def test_strip_empty_g():
	# strip empty <g>
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-1"><path></path></g><g id="layer-2"><path></path></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><g id="foo"><path/></g></svg>'''))

def test_strip_empty_layer():
	# strip empty layer
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-3"><path></path></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><g id="foo"></g></svg>'''))
		c.pop_group()
		c.push_group('layer-3')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><g id="foo"><path/></g></svg>'''))

def test_set_root_id():
	# set id of root <svg>
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg" id="newroot"><g id="layer-1"><path></path></g><g id="layer-2"><path></path></g></svg>''',
		root_id="newroot",
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg" id="root"><path/></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg" id="removed"><path/></svg>'''))
		c.pop_group()

def test_combine_same_layer():
	# same layers are combined
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer"><path></path><path></path></g><g id="other-layer"><path></path></g></svg>'''
	) as c:
		c.push_group('layer')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))
		c.pop_group()
		c.push_group('other-layer')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'''))
		c.pop_group()


def test_remove_background_rect_exept_first():
	# remove background rects, but keep first rect
	with check_combine(
	    '''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-1"><path></path><rect y="0" x="0" style="fill: black"></rect></g><g id="layer-2"><path></path></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/><rect x="0" y="0" style="fill: black"/></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path/><rect x="0" y="0" style="fill: yellow"/></svg>'''))
		c.pop_group()

def test_tree():
	# same layers are combined
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-1"><path name="1"></path></g><g id="layer-2"><path name="2"></path><g id="layer-2a"><path name="2a"></path></g><path name="2"></path></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path name="1"/></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path name="2"/></svg>'''))
		c.push_group('layer-2a')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path name="2a"/></svg>'''))
		c.pop_group()
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path name="2"/></svg>'''))
		c.pop_group()

def test_tree_empty():
	# empty sub trees are note added
	with check_combine(
		'''<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg"><g id="layer-2"><g id="layer-2a"><path name="2a"></path></g></g></svg>'''
	) as c:
		c.push_group('layer-1')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"></svg>'''))
		c.pop_group()
		c.push_group('layer-2')
		c.push_group('layer-2a')
		c.add(BytesIO('''<svg xmlns="http://www.w3.org/2000/svg"><path name="2a"/></svg>'''))
		c.pop_group()

import contextlib
@contextlib.contextmanager
def check_combine(result, root_id=None):
	out = BytesIO()
	c = CombineSVG(out, root_id=root_id)

	yield c
	# for input in inputs:
	# 	c.push_group(input['name'])
	# 	c.add(BytesIO(input['content']))
	# 	c.pop_group()

	c.close()

	out.seek(0)
	assert result == out.read().replace('\n', '')
