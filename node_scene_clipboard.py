from collections import OrderedDict
from node_graphic_link import QDMGraphicsLink
from node_node import Node
from node_link import Link, LINK_TYPE_BEIZER

DEBUG = True

class SceneClipboard():
  """docstring for SceneClipboard"""
  def __init__(self, scene):
    self.scene = scene

  def serializeSelected(self,delete=False):
    if DEBUG: print('node_scene_clipboard :: -- COPY to Clipboard --')

    # sel = self.scene.grScene.selectedItems()
    sel_nodes, sel_links = [],[]
    sel_sockets = {}

    # sort links and nodes
    for item in self.scene.grScene.selectedItems():
      if hasattr(item,'node'):
        sel_nodes.append(item.node.serialize())
        if DEBUG:print('node_scene_clipboard :: input -- output in clipboard',(item.node.inputs + item.node.outputs))
        for socket in (item.node.inputs + item.node.outputs):
          if DEBUG:print('node_scene_clipboard :: hit loop',socket)
          sel_sockets[socket.id] = socket

      elif isinstance(item, QDMGraphicsLink):
        sel_links.append(item.link)
          
    # debug
    if DEBUG:
      print(' NODES\n  ',sel_nodes)
      print(' LINKS\n  ',sel_links,)
      print(' SOCKETS\n  ',sel_sockets)

    # remove link that is not connected
    links_to_remove = []
    for link in sel_links:
      if link.start_socket.id in sel_sockets and link.end_socket.id in sel_sockets:
        if DEBUG: print('node_scene_clipboard :: link is ok, connected with both sides')
        pass
      else:
        if DEBUG: print('node_scene_clipboard :: link',link,'is not connected with both sides')
        links_to_remove.append(link) 

    for link in links_to_remove:
      sel_links.remove(link) 


    # make final list of links
    links_final = []
    for link in sel_links:
      links_final.append(link.serialize())    
  

    data = OrderedDict([
        ('nodes',sel_nodes),
        ('links',links_final)
      ])

    if delete:
      self.scene.grScene.views()[0].deleteSelected() #Returns a list of all the views that display this scene.
      self.scene.history.storeHistory('node_scene_clipboard :: Cut element from scene',setModified=True)

    if DEBUG: print('node_scene_clipboard ::',data)  

    return data

  def deserializeFromClipboard(self,data):
    hashmap = {}

    # paste on mouse pointer
    view = self.scene.grScene.views()[0]
    mouse_scene_pos = view.last_scene_mouse_position
    #  
    # claculate scene object + center
    minx,maxx,miny,maxy = 0,0,0,0
    for node_data in data['nodes']:
      x, y = node_data['pos_x'], node_data['pos_y']
      if x < minx: minx = x
      if x > maxx: maxx = x
      if y < miny: miny = y
      if y > maxy: maxy = y

    bbox_center_x = (minx + maxx)/2
    bbox_center_y = (miny + maxy)/2   

    center = view.mapToScene(view.rect().center())
    
    # calculate offset
    offset_x = (mouse_scene_pos.x() - bbox_center_x)
    offset_y = (mouse_scene_pos.y() - bbox_center_y)

    if DEBUG: print('node_scene_clipboard ::',data)

    # create each node
    for node_data in data['nodes']:
      new_node = Node(self.scene) 
      new_node.deserialize(node_data, hashmap, restore_id=False)

      # read just the new node's position
      pos = new_node.pos
      new_node.setNodePos(pos.x() + offset_x, pos.y() + offset_y)

    # create each links
    if 'links' in data:
      for link_data in data['links']:
        new_link = Link(self.scene)
        new_link.deserialize(link_data,hashmap,restore_id=False)


    # store history
    self.scene.history.storeHistory('node_scene_clipboard :: Pasted Elements in scene',setModified=True)
