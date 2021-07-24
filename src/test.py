tree =  {'children': [{'label': 1, 'value': 1},
  {'children': [{'label': 2, 'value': 1},
    {'value': 2, 'label': 4},
    {'value': 3, 'label': 4},
    {'label': 5, 'value': 4},
    {'label': 3, 'value': 5},
    {'children': [{'value': 1, 'label': 4},
      {'value': 2, 'label': 4},
      {'label': 4, 'value': 3},
      {'label': 4, 'value': 4},
      {'value': 5, 'label': 4},
      {'label': 5, 'value': 6}],
     'label': None,
     'value': 6,
     'key': 'in_strength'}],
   'label': None,
   'value': 2,
   'key': 'out_strength'},
  {'children': [{'value': 1, 'label': 5},
    {'value': 2, 'label': 5},
    {'value': 3, 'label': 5},
    {'label': 5, 'value': 4},
    {'children': [{'value': 1, 'label': 5},
      {'value': 2, 'label': 5},
      {'value': 3, 'label': 5},
      {'label': 4, 'value': 4},
      {'label': 5, 'value': 5},
      {'value': 6, 'label': 5}],
     'label': None,
     'value': 5,
     'key': 'in_strength'},
    {'label': 4, 'value': 6}],
   'label': None,
   'value': 3,
   'key': 'out_degree'},
  {'children': [{'value': 1, 'label': 4},
    {'value': 2, 'label': 4},
    {'label': 5, 'value': 3},
    {'label': 4, 'value': 4},
    {'label': 6, 'value': 5},
    {'children': [{'value': 1, 'label': 4},
      {'value': 2, 'label': 4},
      {'value': 3, 'label': 4},
      {'value': 4, 'label': 4},
      {'children': [{'value': 1, 'label': 4},
        {'value': 2, 'label': 4},
        {'value': 3, 'label': 4},
        {'value': 4, 'label': 4},
        {'label': 5, 'value': 5},
        {'label': 4, 'value': 6}],
       'label': None,
       'value': 5,
       'key': 'out_degree'},
      {'children': [{'value': 1, 'label': 4},
        {'value': 2, 'label': 4},
        {'value': 3, 'label': 4},
        {'value': 4, 'label': 4},
        {'label': 4, 'value': 5},
        {'label': 4, 'value': 6}],
       'label': None,
       'value': 6,
       'key': 'out_degree'}],
     'label': None,
     'value': 6,
     'key': 'in_strength'}],
   'label': None,
   'value': 4,
   'key': 'out_strength'},
  {'children': [{'value': 1, 'label': 6},
    {'label': 4, 'value': 2},
    {'value': 3, 'label': 6},
    {'label': 5, 'value': 4},
    {'value': 5, 'label': 6},
    {'children': [{'value': 1, 'label': 6},
      {'value': 2, 'label': 6},
      {'value': 3, 'label': 6},
      {'value': 4, 'label': 6},
      {'children': [{'value': 1, 'label': 6},
        {'value': 2, 'label': 6},
        {'value': 3, 'label': 6},
        {'value': 4, 'label': 6},
        {'label': 5, 'value': 5},
        {'label': 6, 'value': 6}],
       'label': None,
       'value': 5,
       'key': 'out_degree'},
      {'label': 6, 'value': 6}],
     'label': None,
     'value': 6,
     'key': 'in_strength'}],
   'label': None,
   'value': 5,
   'key': 'out_strength'},
  {'children': [{'value': 1, 'label': 6},
    {'value': 2, 'label': 6},
    {'value': 3, 'label': 6},
    {'value': 4, 'label': 6},
    {'label': 5, 'value': 5},
    {'children': [{'value': 1, 'label': 6},
      {'value': 2, 'label': 6},
      {'value': 3, 'label': 6},
      {'value': 4, 'label': 6},
      {'label': 6, 'value': 5},
      {'label': 6, 'value': 6}],
     'label': None,
     'value': 6,
     'key': 'out_degree'}],
   'label': None,
   'value': 6,
   'key': 'out_strength'}],
 'label': None,
 'value': None,
 'key': 'in_degree'}

import copy

def generateList(tree):
    decisionList = [{}]

    def recursion_fn(tree, decisionList=[]):

        if tree["label"] is not None:
            decisionList[-1]["label"] = tree["label"]

        else:
            prefix = copy.deepcopy(decisionList[-1])

            for j, subTree in enumerate(tree["children"]):
                if j > 0:
                    decisionList.append(prefix)

                decisionList[-1][tree["key"]] = subTree["value"]
                recursion_fn(subTree, decisionList)

    recursion_fn(tree, decisionList)

    return decisionList
  
print(generateList(tree))
