class Serializable():
  def __init__(self):
    self.id = id(self)

  def serialize(self):
    raise NotImplemented('serialize not implemented')

  def deserialize(self, data, hashmap={}):  
    raise NotImplemented('deserialize not implemented') 
