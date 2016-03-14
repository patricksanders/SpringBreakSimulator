import random

class GeneratorDict(object):

    def __init__(self, text, order, output_count):
        self.text = text
        self.order = order
        self.seed_counts = {}
        self.output_count = output_count


    def read_text(self):
        words = self.text.split()

        index = 0
        bound = len(words) - (self.order + 1)

        for token in self.text:
            seed = tuple(words[index:index+self.order])
            next_word = words[index+self.order]

            if seed in self.seed_counts:
                self.seed_counts[seed].append(next_word)

            else:
                self.seed_counts[seed] = [next_word]

            index += 1
            if index == bound:
                return self.seed_counts

    # write markov text given a number of characters for output
    def output_text(self):

        print "choosing random start seed"
        start_seed = random.choice(self.seed_counts.keys())
        print "start seed is", start_seed
        size = len(" ".join(start_seed))
        print "size of start seed is", size

        output_list = list(start_seed)

        while(True):
            if start_seed in self.seed_counts:
                next_seed = random.choice(self.seed_counts[start_seed])
                print "next seed is", next_seed
                size += len(" ".join(next_seed)) + 1
                if size < self.output_count:
                    output_list.append(next_seed)
                    start_seed = tuple(output_list[-self.order:])
                else:
                    break

        return " ".join(output_list)[0:self.output_count]

