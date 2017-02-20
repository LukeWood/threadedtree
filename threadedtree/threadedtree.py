'''
This file is part of Threadedtree.

Threadedtree is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Threadedtree is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with threadedtree.  If not, see <http://www.gnu.org/licenses/>.
'''

import treenodes

class ThreadedTree(object):
	def __init__(self, iterable=[], root=None, duplicate_strategy="stack"):
		"""Creates an empty threaded tree.

		Duplicate Strategy:
		stack - aggregate duplicate keys using an integer
		duplicate - allow duplicate nodes in tree
		"""
		self.root = root
		self._len = 0
		self.duplicate_strategy = duplicate_strategy
		self.del_both = 0
		self.del_none = 0
		self.del_right = 0
		self.del_left = 0
		self.del_root = 0
		self.called = 0
		if iterable:
			for val in iterable:
				self.insert(val)

	def __len__(self):
		return self._len

	def __repr__(self):
		return str(list(self.in_order()))

	def __eq__(self, other):
		return list(self.in_order) == list(other.in_order())

	def __ne__(self, other):
		return list(self.in_order) != list(other.in_order())

	def __lt__(self, other):
		return NotImplemented

	def __le__(self, other):
		return NotImplemented

	def __gt__(self, other):
		return NotImplemented

	def __ge__(self, other):
		return NotImplemented

	def __hash__(self):
		return hash(tuple(list(t.in_order())))

	def __add__(self, other):
		first = list(other.in_order())
		first.extend(list(self.in_order()))
		return ThreadedTree(first)

	def __sub__(self, other):
		first = ThreadedTree(self.in_order())
		for val in other.in_order():
			first.remove(val)
		return first


	def _new_node(self, value):
		"""Seperated into a method so that we can return different types of nodes for different situations"""
		return treenodes.Threaded_Tree_Node(value)

	def insert(self, value):
		"""Inserts a new node containing 'value' into the tree."""
		self._len += 1

		if self.root == None:
			self.root = self._new_node(value)
			return

		current = self.root
		directionLeft = False
		directionRight = False

		while True:
			if current.val > value:
				if not current.lthreaded:
					#Add as left child
					directionLeft = True
					directionRight = False
					break
				else:
					current = current.left
			elif current.val < value:
				if not current.rthreaded:
					directionLeft = False
					directionRight = True
					break
				else:
					current = current.right

		if directionLeft:
			new_node = self._new_node(value)
			new_node.left = current.left
			current.left = new_node
			new_node.lthreaded = current.lthreaded
			current.lthreaded = True
			new_node.right = current
		elif directionRight:
			new_node = self._new_node(value)
			new_node.right = current.right
			current.right = new_node
			new_node.rthreaded = current.rthreaded
			current.rthreaded = True
			new_node.left = current

	def find(self, value):
		current = self.root
		while True:
			if current.val > value:
				if current.lthreaded:
					current = current.left
				else:
					return False
			elif current.val < value:
				if current.rthreaded:
					current = current.right
				else:
					return False
			else:
				return True

	def remove(self, value):
		if self._len > 0 and self._remove(value): #take advantage of python short circuiting
			self._len -= 1
			return True
		return False

	def _remove(self, value):
		if value == self.root.val:
			return self._delete_root()

		current = parent = self.root
		while True:
			if current.val > value:
				if current.lthreaded:
					parent = current
					current = current.left
				else:
					return False
			elif current.val < value:
				if current.rthreaded:
					parent = current
					current = current.right
				else:
					return False
			else:
				break
		if current.lthreaded == False and current.rthreaded == False:
			return self._delete_with_no_children(current)
		elif current.lthreaded == True and current.rthreaded == True:
			return self._delete_with_both_children(current, parent)
		elif current.lthreaded:
			return self._delete_with_left_child(current, parent)
		else:
			return self._delete_with_right_child(current, parent)

	def _delete_root(self):
		self.del_root += 1
		if self._len == 1:
			self.root = None
			return True
		if self.root.right == None:
			if not self.root.left.rthreaded:
				self.root.left.right = None
			else:
				far_right = self.root.left
				while far_right.right != self.root:
					far_right = far_right.right
				far_right.right = None
			new_root = self.root.left
			del self.root
			self.root = new_root
			return True
		elif not self.root.left:
			if not self.root.right.lthreaded:
				self.root.right.left = None
			else:
				far_left = self.root.right
				while far_left.left != self.root:
					far_left = far_left.left
				far_left.left = None
			new_root = self.root.right
			del self.root
			self.root = new_root
			return True

		new_root = self.root.right
		far_left = new_root
		while far_left.left != self.root:
			far_left = far_left.left

		far_right = self.root.left
		while far_right.right != self.root:
			far_right = far_right.right


		far_left.lthreaded = True
		far_left.left = self.root.left
		far_right.right = far_left
		del self.root
		self.root = new_root
		return True

	def _delete_with_both_children(self, current, parent):
		self.del_both += 1
		on_right = False
		if parent.right == current:
			on_right = True

		far_left = current.right
		while far_left.left != current:
			far_left = far_left.left
		far_left.left = current.left
		far_left.lthreaded = current.lthreaded

		far_right = current.left
		while far_right.right != current:
			far_right = far_right.right

		far_right.right = far_left
		
		if on_right:
			parent.right = current.right
		else:
			parent.left = current.right
		del current
		return True

	def _delete_with_no_children(self, current):
		self.del_none += 1
		if current.left == None:
			current.right.lthreaded = False
			current.right.left = None
			del current
			return True
		elif current.right == None:
			current.left.rthreaded = False
			current.left.right = None
			del current
			return True
		else:
			if current.left.right == current:
				current.left.rthreaded = False
				current.left.right = current.right
				del current
				return True
			else:
				current.right.lthreaded = False
				current.right.left = current.left
				del current
				return True

	def _delete_with_left_child(self, current, parent):
		self.del_left += 1
		far_right = current.left
		while far_right.right != None and far_right.right != current:
			far_right = far_right.right
		far_right.right = current.right

		on_right = False
		if parent.right == current:
			on_right = True

		if on_right:
			parent.right = current.left
		else:
			parent.left = current.left

		del current
		return True

	def _delete_with_right_child(self, current, parent):
		self.del_right += 1
		far_left = current.right
		while far_left.left != None and far_left.left != current:
			far_left = far_left.left
		far_left.left = current.left

		on_right = False
		if parent.right == current:
			on_right = True

		if on_right:
			parent.right = current.right
		else:
			parent.left = current.right
		del current
		return True

	def in_order(self):
		if self._len > 0:
			current = self.root
			while current.lthreaded:
				current = current.left
			while current != None:
				yield current.val
				current = self._find_next_in_order(current)

	def _find_next_in_order(self, node):
		if not node.rthreaded:
			return node.right

		node = node.right

		while node.lthreaded:
			node = node.left
		return node

if __name__ == "__main__":
	'''
	import random, copy
	upper_bound = 2000
	samples = 1000
	trials = 1
	t = ThreadedTree()
	for i in xrange(trials):
		print "Trial",i,":",
		test_suite = random.sample(range(upper_bound), samples)
		print "insert ->",
		for val in test_suite:
			t.insert(val)
		print "[done]","delete->",
		vals_to_delete = copy.deepcopy(test_suite)
		random.shuffle(vals_to_delete)
		try:
			for val in vals_to_delete:
				test_suite.remove(val)
				t.remove(val)
				test_suite.sort()
				assert(test_suite ==  list(t.in_order())),"Lists are not equivalent"
		except:
			print
			print test_suite
			print vals_to_delete
			print val
			raise
		print "[done]"
	
		print "DEL root:", t.del_root
		print "DEL both:", t.del_both
		print "DEL none:", t.del_none
		print "DEL rigt:", t.del_right
		print "DEL left:", t.del_left
		print "Called:", t.called
	t = ThreadedTree()
	t.insert(10)
	t.insert(45)
	t.insert(91)
	t.insert(64)
	t.insert(12)
	print list(t.in_order())
	print
	selection = None
	while selection != -1:
		selection = raw_input("Val to delete: ")
		print t.remove(int(selection)), list(t.in_order())
	'''
	import random
	import time
	arr = random.sample(range(10000),10000)
	start = time.time()
	s = ThreadedTree(arr)
	end = time.time()
	print "Took:", end-start
	start = time.time()
	s = sorted(arr)
	end = time.time()
	print "Took:", end - start
	t = ThreadedTree([1,2,3])
	s = ThreadedTree([4,5,6])
	p = ThreadedTree([6,1])
	x = t + s
	print x
	x -= p
	print x
	print ThreadedTree(["abc","def","cat","dog"])