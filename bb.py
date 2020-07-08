import queue
from copy import deepcopy

STEP_OUTPUT = 500


class ZerosTape(object):

    def __init__(self):
        self.__tape_positive = []
        self.__tape_negative = []

    def __str__(self):
        s = ""

        for symbol in reversed(self.__tape_negative):
            s += str(symbol)

        for symbol in self.__tape_positive:
            s += str(symbol)

        return s

    def __getitem__(self, index):
        if index >= 0:
            if index >= len(self.__tape_positive):
                return 0
            else:
                return self.__tape_positive[index]
        else:  # index < 0
            index = abs(index) - 1
            if index >= len(self.__tape_negative):
                return 0
            else:
                return self.__tape_negative[index]

    def __setitem__(self, index, symbol):
        if index >= 0:
            if index < len(self.__tape_positive):
                self.__tape_positive[index] = symbol
            elif index == len(self.__tape_positive):
                self.__tape_positive.append(symbol)
            else:
                print("The space in the tape has occurred.")
                exit(31)
        else:  # index < 0
            index = abs(index) - 1
            if index < len(self.__tape_negative):
                self.__tape_negative[index] = symbol
            elif index == len(self.__tape_negative):
                self.__tape_negative.append(symbol)
            else:
                print("The space in the tape has occurred.")
                exit(31)


class TuringMachine(object):

    def __init__(self, initial_state=1, final_states=None, transition_function=None, machine_id=0):
        self.__id = machine_id
        self.__tape = ZerosTape()
        self.__head_position = 0
        self.__current_state = initial_state

        if transition_function is None:
            self.__transition_function = {}
        else:
            self.__transition_function = transition_function

        if final_states is None:
            self.__final_states = set()
        else:
            self.__final_states = set(final_states)

        self.__steps_counter = 0

    def get_tape(self):
        return "..." + str(self.__tape) + "..."

    def step(self):
        symbol_under_head = self.__tape[self.__head_position]
        read_from_tape = (self.__current_state, symbol_under_head)

        if read_from_tape in self.__transition_function:
            write_to_tape = self.__transition_function[read_from_tape]

            self.__tape[self.__head_position] = write_to_tape[0]

            if write_to_tape[1] == "R":
                self.__head_position += 1
            elif write_to_tape[1] == "L":
                self.__head_position -= 1

            self.__current_state = write_to_tape[2]

            self.__steps_counter += 1

            return 0
        else:
            return -1  # halt undefined transition

    def set_id(self, machine_id):
        self.__id = machine_id

    def in_final_state(self):
        if self.__current_state in self.__final_states:
            return True
        else:
            return False

    def add_transition(self, transition):
        self.__transition_function.update(transition)

    def local_configuration(self):
        return self.__current_state, self.__tape[self.__head_position]

    def transition_function(self):
        return self.__transition_function

    def steps_number(self):
        return self.__steps_counter

    def id(self):
        return self.__id

    def steps_count(self):
        return self.__steps_counter


def upper_bound_heuristic(states_number, symbols_number, bb_steps):
    if bb_steps == 0:
        return states_number * symbols_number * 3
    else:
        return bb_steps * 2


def bb(states_number, symbols_number):

    hash_machines = {}
    queue_machines = queue.Queue()
    bb_steps = 0
    bb_machine = None

    M_1 = TuringMachine(1, [0], {(1, 0): (1, "R", 2)})
    queue_machines.put(M_1)

    machines_counter = 1

    bb_steps_prev_iter = -1
    while bb_steps != bb_steps_prev_iter:
        bb_steps_prev_iter = bb_steps
        upper_bound = upper_bound_heuristic(states_number, symbols_number, bb_steps)
        print("bb_steps:", bb_steps)
        print("upper_bound:", upper_bound)
        for machine_id in hash_machines:
            queue_machines.put(hash_machines[machine_id])

        while not queue_machines.empty():
            M = queue_machines.get()

            if M.id() % STEP_OUTPUT == 0:
                print("Analyzing machine with id", M.id())

            # for a single machine
            while M.steps_number() < upper_bound:
                if M.in_final_state():
                    if M.steps_number() > bb_steps:  # new lower bound
                        bb_machine = M
                        bb_steps = M.steps_number()
                        print("new_candidate:", bb_steps)
                    hash_machines.pop(M.id())
                    break
                elif M.step() == -1:  # halt undefined transition
                    hash_machines.pop(M.id(), 0)
                    # add new machines

                    # transition function can not contain more then one halt rules
                    if not (len(M.transition_function()) == states_number * symbols_number - 1 and
                       sum(value == (0, "R", 0) for value in M.transition_function().values()) == 0):

                        for symbol in range(0, symbols_number):
                            for state in range(1, states_number + 1):
                                for move in ("L", "R"):
                                    M_new = deepcopy(M)
                                    M_new.set_id(machines_counter)

                                    M_new.add_transition({M.local_configuration(): (symbol, move, state)})

                                    hash_machines.update({M_new.id(): M_new})
                                    queue_machines.put(M_new)

                                    machines_counter += 1
                                    if machines_counter % STEP_OUTPUT == 0:
                                        print(machines_counter, "machines discovered")

                    # add halt only to (0, "R", 0) if it is not added yet
                    M_new = deepcopy(M)
                    M_new.set_id(machines_counter)

                    M_new.add_transition({M.local_configuration(): (0, "R", 0)})

                    hash_machines.update({M_new.id(): M_new})
                    queue_machines.put(M_new)

                    machines_counter += 1

                    if machines_counter % STEP_OUTPUT == 0:
                        print(machines_counter, "machines discovered")

                    break

    return bb_steps, bb_machine


def main():
    states_input = 2
    symbols_input = 3
    print("Searching for BB(", states_input, ", ", symbols_input, ")", sep="")
    steps_number, machine = bb(states_input, symbols_input)
    print("-----result-----")
    print("steps_number: ", steps_number, sep="")
    print("machine_transition_function: ", machine.transition_function(), sep="")


if __name__ == "__main__":
    main()
