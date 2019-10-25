from node_graphic_link import QDMGraphicsLink

DEBUG = True

class SceneHistory():
  def __init__(self,scene):
    self.scene = scene

    self.history_stack = []
    self.history_current_step = -1
    self.history_limit = 8

  def undo(self):
    if DEBUG: print('node_scene_history :: UNDO')

    if self.history_current_step > 0:
      self.history_current_step -= 1
      self.restoreHistory()

  def redo(self):
    if DEBUG: print('node_scene_history :: REDO')

    if self.history_current_step +1 < len(self.history_stack):
      self.history_current_step += 1
      self.restoreHistory()

  def restoreHistory(self):
    if DEBUG: 
      print('node_scene_history :: Restore History ... current_step: {},({})'.format(
        self.history_current_step,
        len(self.history_stack)
        )
      )  

      self.restoreHistoryStamp(self.history_stack[self.history_current_step])

  def storeHistory(self, description,setModified = False):
    if setModified:
      self.scene.has_been_modified = True
    if DEBUG: 
      print('node_scene_history :: Storing History {} ... current_step: {},({})'.format(
        description,
        self.history_current_step,
        len(self.history_stack)
        )
      )  

      # pointer is not at the end of the stack
      if self.history_current_step +1 < len(self.history_stack):
        self.history_stack = self.history_stack[0:self.history_current_step+1]

      # set history limit
      if self.history_current_step+1 >= self.history_limit:
        self.history_stack = self.history_stack[1:]
        self.history_current_step -= 1


      hs = self.createHistoryStamp(description)
      if DEBUG and hs is not None: print('trigger store hs')

      self.history_stack.append(hs)
      self.history_current_step += 1
      if DEBUG: print("node_scene_history ::  -- setting step to:",self.history_current_step)

  def createHistoryStamp(self,description):
    sel_obj = {
      'nodes' : [],
      'links' : [],
    }

    for item in self.scene.grScene.selectedItems():
      if hasattr(item, 'node'):
        sel_obj['nodes'].append(item.node.id)
      elif isinstance(item,QDMGraphicsLink):
        sel_obj['links'].append(item.link.id)
        

    history_stamp = {
      'description' : description,
      'snapshot' : self.scene.serialize(),
      'selection': sel_obj
    }

    return history_stamp

  def restoreHistoryStamp(self, history_stamp):
    if DEBUG: print('node_scene_history :: RHS',history_stamp['description'])

    self.scene.deserialize(history_stamp['snapshot'])

    # restore selection
    for link_id in history_stamp['selection']['links']:
      for link in self.scene.links:
        if link.id == link_id:
          link.grLink.setSelected(True)
          break

    for node_id in history_stamp['selection']['nodes']:
      for node in self.scene.nodes:
        if node.id == node_id:
          node.grNode.setSelected(True)
          break      
