from struct import *

################# Function definition ######################

def parse_desc(node_offset):
	f.seek(node_offset)
	node_desc = f.read(14)
	flink = unpack_from('>I',node_desc,0x00)[0]
	blink = unpack_from('>I',node_desc,0x04)[0]
	type_info = unpack_from('>B',node_desc,0x08)[0]
	height = unpack_from('>B',node_desc,0x09)[0]
	rec_num = unpack_from('>H',node_desc,0x0a)[0]
	return flink, blink, type_info, height, rec_num

def _record_type(node_type, node_offset, i, option):
	type_info = node_type
	if type_info == 0xFF:
		traverse_leaf(node_offset,i)
	elif type_info == 0:
		traverse_index(node_offset,i, option)
	elif type_info == 1:
		print "Header node"
	elif type_info == 2:
		print "Map node"

def read_desc(start_offset,i, flag):
	rec_ptr = start_offset + int(node_size,16)-(i+1)*2
	f.seek(rec_ptr)
	rec_offset = hex(unpack_from('>H',f.read(2),0x00)[0])
	offset = int(rec_offset,16) + start_offset
	f.seek(offset)
	record = f.read(8)
	keyname_len = unpack_from('>H',record,0x06)[0]*2
	keyname = f.read(keyname_len)
	a = str(keyname_len)+"s"
	keyname_ = unpack_from(a,keyname,0x00)[0]
	if keyname_len != 0:
		parent_id = unpack_from('>I',keyname,0x02)[0]
		print "[-] ",i," record"
		print "    file(folder) name :",keyname.decode('utf-16-be')
		print "    parent node ID : ",hex(parent_id)

		if flag != 0:
			b = int(hex(unpack_from('>H',f.read(2),0x00)[0]),16)
			if b == 0x1:
				record_type = "folder"
				dum = f.read(0x58)
				folderID = unpack_from('>I',dum,0x08)[0]
				print "    CNID : ",hex(folderID)
			elif b == 0x2:
				record_type = "file"
				dum = f.read(0xd8+0x50)
				fileID = unpack_from('>I',dum,0x08)[0]
				print "    CNID : ",hex(fileID)
			elif b == 0x3:
				record_type = "folder thread"
			elif b == 0x4:
				record_type = "file thread"

			print "    record type : ",record_type

def traverse_index(start_offset,i, option):
	read_desc(start_offset,i, 0)
	if int(option,10) == 2:
		child_ptr = hex(unpack_from('>I',f.read(4),0x00)[0])
		child_node_offset = catalog_header + int(node_size,16)*int(child_ptr,16)
		#print child_node_offset,type(child_node_offset)
		child_node = parse_desc(child_node_offset)
		for j in range(child_node[4]):
			_record_type(child_node[2],child_node_offset,j,option)
	

def traverse_leaf(start_offset,i):
	read_desc(start_offset,i, 1)
	#print hex(f.tell())
	#record_type = f.read(2)
	#print "record type : ",record_type


################# Main Start ######################

f = open('hfsx_image','rb')

f.seek(1024)

data = f.read(512)

sign = hex(unpack_from('>H',data,0x00)[0])
block_size = hex(unpack_from('>I',data,0x28)[0])
total_block = hex(unpack_from('>I',data,0x2c)[0])


print "\n\n[+] Volume Header\n"
print "signature : ",sign
print "block size : ",block_size
print "total blocks : ",total_block

catalog = data[0x110:0x110+80]

logic_size = hex(unpack_from('>Q',catalog,0x00)[0])
clumpSize = hex(unpack_from('>I',catalog,0x08)[0])
total_blk = hex(unpack_from('>I',catalog,0x0c)[0])

print "\n\n[+] Catalog File\n"
print "logical size : ",logic_size
print "clump size : ",clumpSize
print "total blocks(file use) : ",total_blk

extent = catalog[0x10:0x10+64]
start_blk = hex(unpack_from('>I',extent,0x00)[0])
block_cnt = hex(unpack_from('>I',extent,0x04)[0])

print "start block : ", start_blk
print "block count : ", block_cnt

catalog_header = int(start_blk,16)*int(block_size,16)
print "\ncatalog header offset : ",hex(catalog_header)

f.seek(catalog_header)
f.seek(14,1)

bt_header = f.read(44)
depth = hex(unpack_from('>H',bt_header,0x00)[0])
root_node = hex(unpack_from('>I',bt_header,0x02)[0])
node_size = hex(unpack_from('>H',bt_header,0x12)[0])
total_node = hex(unpack_from('>I',bt_header,0x16)[0])

print "\n[+] BT Header\n"
print "depth : ",depth
print "root node : ",root_node
print "node size : ",node_size
print "total_node : ",total_node

rootnode_offset = catalog_header + int(root_node,16)*int(node_size,16)
print "root node offset : ",hex(rootnode_offset)

node = parse_desc(rootnode_offset) #flink / blink / type / height / record number
if node[2] == -1:
	print "node type : Leaf node"
elif node[2] == 0:
	print "node type : Index node"
elif node[2] == 1:
	print "node type : Header node"
elif node[2] == 2:
	print "node type : Map node"


print "\n[*] select mode\n"
print "\n\t1. print record in root node"
print "\n\t2. print everything\n"

d = raw_input('>')

for i in range(node[4]):
	print "\n==================================================================="
	print "[+] ",i," th record in root node"
	_record_type(node[2],rootnode_offset,i,d)
	print "==================================================================="

