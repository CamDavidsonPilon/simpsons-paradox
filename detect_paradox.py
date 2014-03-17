# detect simpson's paradox
import numpy as np
import pandas as pd


def aggregate_data(df, conversion_col, treatment_col, segment_col):
    """
    takes table of individual level data and aggregates it for simpsons paradox detection.

    conversion_col is 1 if success, 0 else. 

    ex:

    pd.DataFrame([
        ['small', 'A', 1],
        ['small', 'B', 0],
        ['large', 'A', 1],
        ['small', 'A', 1],
        ['large', 'B', 0],
        ['large', 'B', 0],
    ], columns=['kidney_stone_size', 'treatment', 'recovery'])   


    """
    df_ = df[[conversion_col, treatment_col, segment_col]]
    gb = df_.groupby([segment_col, treatment_col]).agg(
        [np.sum, lambda x: len(x)])
    gb.columns = [conversion_col, "total"]

    return gb.reset_index()


def simpsons_paradox(df, conversion_col, total_col, treatment_col, segment_col):
    """
    given a dataframe like:
        pd.DataFrame([
            ['small', 'A', 81, 87],
            ['small', 'B', 234, 270],
            ['large', 'A', 192, 263],
            ['large', 'B', 55, 80],
        ], columns=['kidney_stone_size', 'treatment', 'recovery', 'total'])   
    will determine if simpsons paradox exists. Non Bayesian!

    > simpsons_paradox( df, 'recovery', 'total', 'treatment', 'kidney_stone_size' )    
    """

    # find global optimal:
    gbs = df.groupby(treatment_col).sum()
    print "## Global rates: "
    print (gbs[conversion_col] / gbs[total_col])
    print
    global_optimal = (gbs[conversion_col] / gbs[total_col]).argmax()

    # check optimal via segments
    df_ = df.set_index([segment_col, treatment_col])
    rates = (df_[conversion_col] / df_[total_col]).unstack(-1)
    print "## Local rates:"
    print rates
    print
    # find the local optimals
    local_optimals = rates.apply(lambda x: x.argmax(), 1)

    if local_optimals.unique().shape[0] > 1:
        print "## Simpsons paradox not detected."
        print "## Segmented rates do not have a consistent optimal choice"
        print "## Local optimals:"
        print local_optimals
        print "## Global optimal: ", global_optimal
        return False

    local_optimal = local_optimals.unique()[0]

    print "## Global optimal: ", global_optimal
    print "## Local optimal: ", local_optimal
    if local_optimal != global_optimal:
        print "## Simpsons Paradox detected."
        return True

    else:
        print "## Simpsons paradox not detected."
        return False


if __name__ == "__main__":
    # create some data, indentical to the data at
    # http://en.wikipedia.org/wiki/Simpsons_paradox
    d = []
    d += ([('A', 'small', 1)] * 81)
    d += ([('A', 'small', 0)] * (87 - 81))
    d += ([('B', 'small', 0)] * (270 - 234))
    d += ([('B', 'small', 1)] * (234))
    d += ([('B', 'large', 1)] * (55))
    d += ([('B', 'large', 0)] * (80 - 55))
    d += ([('A', 'large', 0)] * (263 - 192))
    d += ([('A', 'large', 1)] * (192))

    df = pd.DataFrame(
        d, columns=['treatment', 'kidney_stone_size', 'recovery'])
    gb = aggregate_data(df, 'recovery', 'treatment', 'kidney_stone_size')
    simpsons_paradox(gb, 'recovery', 'total', 'treatment', 'kidney_stone_size')
