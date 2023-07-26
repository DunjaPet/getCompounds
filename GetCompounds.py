import pubchempy as pcp
import pandas as pd

# The function shoud get a list of compound names for which you want to get data from PubChem

comp_names =  ["Adenosine","Adenocard","BG8967","Bivalirudin","BAYT006267","diflucan","ibrutinib","PC-32765"]

# Get data from pubChem API and arrange a df

def GetCompData(name_list):

    norm = []
    p = []

   
    for c in name_list:

        cid = pcp.get_cids (c, 'name')
        p.append(pcp.get_properties('CanonicalSMILES,XLogP,MolecularWeight,HBondDonorCount,HBondAcceptorCount', cid, 'cid'))
        comp = pcp.Compound.from_cid(cid)
        norm.append(comp.synonyms[0].upper())


    # create df from lists

    list_of_tuples = list(zip(comp_names, norm, p))   
    df = pd.DataFrame(list_of_tuples, columns=['org_form', 'norm_form', 'p'])

    # flatten df

    df['p'] = df['p'].apply( lambda x: x.pop(0))
    expanded_df = df['p'].apply(pd.Series)
    result_df = pd.concat([df, expanded_df], axis=1)
    result_df.drop(columns=['p'], inplace=True)
    
    return result_df


compounds = GetCompData(comp_names)

# Ranking the compounds by Lipinsky rule of 5

# Lipinski’s Rule of 5 recommendations which predicts the drug-likeness of a new synthetic compound. According to Lipinski’s Rule of 5, an oral drug should have a LogP value <5, ideally between 1.35-1.8 for good oral and intestinal absorption.
# According to Lipinski's rule of five, an orally active drug typically has the following prop- erties: A molecular weight less than 500 g/mol • No more than 5 hydrogen bond donors • No more than 10 hydrogen bond acceptors • An octanol-water partition coefficient (log P) that does not exceed 5


compounds['MolecularWeight'] = compounds['MolecularWeight'].astype(float)


# Define custom ranges and corresponding ranks

rangesXLogP = [-10, 0, 2, 4, float('inf')]
ranksXlogP = [3, 1, 2, 4]
compounds['RankXlogP'] = pd.cut(compounds['XLogP'], bins=rangesXLogP, labels=ranksXlogP, right=False)


# Rank the rest of columns ascending

compounds['RankMW'] = compounds['MolecularWeight'].rank(method='dense')
compounds['RankED'] = compounds['HBondDonorCount'].rank(method='dense')
compounds['RankEA'] = compounds['HBondAcceptorCount'].rank(method='dense')


# Compute TotalRank as min of all other ranks and sort df by it

def add_columns(row):
    return row['RankXlogP'] + row['RankMW'] + row['RankED'] + row['RankEA'] 
compounds['TotalRank'] = compounds.apply(add_columns, axis=1).rank(method='dense')
compounds.sort_values(by='TotalRank')


# write df to Excel file

compounds.to_excel("compounds.xlsx")

