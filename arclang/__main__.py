from . import *

def example():
  with whitepage() as out:
    with center():
      with tab():
        prrow("id", "name")
        prrow(1, "Shawn")
        prrow(2, "Emily")
    return out

if __name__ == "__main__":
  print(html(example()))

