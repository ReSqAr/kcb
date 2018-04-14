import collections
import textwrap


def print_blue(*args, **kwargs):
    new_args = ["\033[1;37;44m"] + list(args) + ["\033[0m"]
    print(*new_args, **kwargs)


def print_red(*args, **kwargs):
    new_args = ["\033[1;37;41m"] + list(args) + ["\033[0m"]
    print(*new_args, **kwargs)


def print_green(*args, **kwargs):
    new_args = ["\033[1;37;42m"] + list(args) + ["\033[0m"]
    print(*new_args, **kwargs)


def print_bold(*args, **kwargs):
    new_args = ["\033[1m"] + list(args) + ["\033[0m"]
    print(*new_args, **kwargs)


def choose(options):
    """
        let the user choose one of the options and call the associated function
        options: dictionary: letter/possible range -> function
    """
    # ask the user what to do (until we have a valid answer)
    while True:
        # build a nice representation of all options
        def convert(inner_option):
            if isinstance(inner_option, range):
                assert inner_option.step == 1, "step has to be 1"
                return "i∊[%d,%d]" % (inner_option.start, inner_option.stop - 1)
            else:
                return str(inner_option)

        opt_text = ",".join(convert(opt) for opt in options.keys())

        # ask question
        answer = input("\033[1mSelect [%s]:\033[0m " % opt_text)

        # find selected option
        selected = options.get(answer)

        # if we found a selected option, call it
        if selected:
            print()
            return selected()

        # otherwise we have a special option
        for option, f in options.items():
            # special options are: range

            # try to interpret answer as a number in the given range
            if isinstance(option, range):
                try:
                    # convert to an integer
                    number = int(answer)
                except ValueError:
                    # if it fails, it cannot be a number
                    continue

                # if it has the right range, select it
                if number in option:
                    print()
                    return f(number)

        # if we are here, the input was invalid
        print("Invalid user input '%s'" % answer)


def ask_questions(questions):
    """
        ask the user the given questions:
        - questions is a list of dictionaries with keys:
            name, description, [default], [postprocessor]
            postprocessor may raise an error if the input is invalid
    """
    # check that we have received questions and questions is a dictionary
    assert questions, "questions has to be non-empty"

    # set default value in answers:
    answers = collections.OrderedDict()
    for question in questions:
        name = question["name"]
        # set
        answers[name] = question.get("default") if question.get("default") else ""

    prefix_length = max(len(question["name"]) for question in questions) + 1

    while True:
        print()
        for question in questions:
            name = question["name"]

            # print the description (wrapped)
            for i, line in enumerate(textwrap.wrap(question["description"], 70)):
                if i == 0:
                    print("\033[1m%s:\033[0m" % name, " " * (prefix_length - len(name) - 1), end="")
                else:
                    print(" " * (prefix_length + 1), end="")
                print(line)

            # ask
            while True:
                inp = input("%s \033[1mnew value [%s]:\033[0m " % (" " * prefix_length, answers[name]))

                # if the input is empty, use the default value
                if not inp:
                    inp = answers[name]

                # strip input, this means you can set '' via entering a space
                inp = inp.strip()

                # post process data
                postprocessor = question.get("postprocessor")
                if postprocessor:
                    try:
                        # apply the postprocessor
                        orig, inp = inp, postprocessor(inp)
                        # if the original version differs from the post processed one,
                        # show it
                        if orig != inp:
                            print(" " * prefix_length, "implicit change to: %s" % (inp,))
                    except Exception as e:
                        # the post processor found an error
                        print(" " * prefix_length, "invalid input: %s" % (e.args[0],))
                        continue

                # if we reach this point, everything is fine, we save the answer
                # and can proceed to the next question
                answers[name] = inp
                break

        print()
        # ask if everything is alright
        x = input("\033[1mAre the above answers correct? Or cancel? [Y/n/c]\033[0m ")

        if x.strip().lower().startswith("c"):
            # if the input starts with c, assume it is cancelled
            return None
        elif x.strip().lower().startswith("n"):
            # if the input starts with 'n', continue
            continue
        else:
            # default: we are done
            break
    print()

    # return the answers
    return answers
