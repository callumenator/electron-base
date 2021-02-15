# webengine

* to prevent the overscroll bounce effect, need this css:
  ```css
  body {
    overscroll-behavior: none;
  }
  ```

* on mac, modifiers are not as expected:
  - command key produces control modifier
  - control key produces meta modifier
  - alt key produces ...
  
* to get events from the webengine, need a workaround
  ```python
  def childEvent(self, event: 'QChildEvent') -> None:
      # This is a workaround for https://bugreports.qt.io/browse/QTBUG-43602
      # We need to grab events from a child of the web engine view - normal
      # method overrides do not work
      if event.added():
          event.child().installEventFilter(self) 
  ``` 