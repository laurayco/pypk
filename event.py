class Event:
  def __init__(self,handlers=None):
    self.handlers=handlers or []
  def __call__(self,*a,**k):
    for eh in self.handlers:
      eh(*a,**k)
