import nuke

def print_knob_names():
    write_node = nuke.createNode('Write')
    for knob in write_node.knobs():
        print(knob, write_node[knob].value())

print_knob_names()
