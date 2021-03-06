import numpy as np
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import auc
def cum_sum(arr):
    """Auxiliary generator to compute cummulative arrays
     (eg. x=[0,1,2]; x_cum=[0,0+1,0+1+2]=[0,1,3])  """
    total=0
    for x in arr:
        total+=x
        yield total

class CMC (object):
    """Calculate the Cumulative Matching Characteristic curve."""
    def __init__(self,similarity_matrix,n_ranks=100,name=None):
        self.similarity_matrix=similarity_matrix
        self.enrrollees=similarity_matrix.columns
        self.users=similarity_matrix.index
        self.n_ranks=n_ranks
        self.__name__=name
        self.cumulative_freq=None

    @property
    def n_ranks(self):
        return self.__nranks
        
    @n_ranks.setter
    def n_ranks(self, n_ranks):
        if n_ranks < 0:
            self.__nranks = 0
        elif n_ranks > len(self.users):
            self.__nranks = len(self.users)
        else:
            self.__nranks = n_ranks

    def is_defined(self,argument):
        if(getattr(self,argument)==None):
            raise ValueError
    def _set_title(self,base_title):
        try:
            self.is_defined("__name__")
            return " ".join([base_title,f"({self.__name__})"])
        except:
            return base_title

    def _users_argsort(self,seq,reverse=True):
        return sorted(self.enrrollees, key=seq.__getitem__,reverse=reverse)[:self.n_ranks]

    def _find_correct_rank(self,user_key):
        try:
            #genuine matching in top n_rank
            return next(rank for rank,user in 
                    enumerate(self.ranks[user_key]) if int(user)==user_key)
        except:
            #genuine matching not in top n_rank
            return None

    def compute_CMC_curve(self):
        """"Compute CMC values for each rank from [1,self.n_ranks]"""
        self.ranks={}
        ranks_freq=np.zeros(self.n_ranks)
        for user in tqdm(self.users):
            self.ranks[user]= self._users_argsort(self.similarity_matrix.loc[user,:])
            #get rank in diagonal
            correct_rank= self._find_correct_rank(user)
            #update freq
            if(not(correct_rank is None)):
                ranks_freq[correct_rank]+=1
        #Normalize
        ranks_freq=ranks_freq/len(self.enrrollees)
        #cumulative frequencies
        cumulative_freq=list(cum_sum(ranks_freq))
        self.cumulative_freq=cumulative_freq

    def _get_rank_cmc(self,rank):
        """ return the CMC of n top ranks"""
        try:
            self.is_defined("cumulative_freq")
        except:
            self.compute_CMC_curve()

        if(rank>self.n_ranks):
            raise ValueError ("You can´t compute the CMC \
                            value of a higher rank for which \
                            you have computed the cumulative frequencies")
        else:
            return self.cumulative_freq[rank-1]

    def plot_CMC_curve(self,ax):
        try:
            self.is_defined("cumulative_freq")
        except:
            self.compute_CMC_curve()
        ranks_arr=range(1,self.n_ranks+1)
        CMC_auc=auc(ranks_arr,self.cumulative_freq)/self.n_ranks
        ax.plot(ranks_arr, self.cumulative_freq, color='darkorange',
                lw=2, label='CMC curve (auc = %0.2f)' % CMC_auc)
        ax.set_xlabel('Rank')
        ax.set_ylabel('Recognition Rate')
        title=self._set_title('Fingerprint detector CMC curve')
        ax.set_title(title)
        ax.legend(loc="lower right")
        # plt.show()


if __name__ == "__main__":
    #Load similarity matrices
    li_sim_file=os.path.join("Li_folder","li_sim_mat.csv")
    # ri_sim_file=os.path.join("Ri_folder","ri_sim_mat.csv")
    li_similarity_matrix=pd.read_csv(li_sim_file).set_index("subject_id")
    # ri_similarity_matrix=pd.read_csv(ri_sim_file).set_index("subject_id")

    # 1) compute the CMC for the first ±100 ranks
    n_ranks = 100
    cmc_obj=CMC(li_similarity_matrix)
    print(f"CMC of first 100 ranks = {cmc_obj._get_rank_cmc(n_ranks)}")

    # 2) plot the probability of recognition in function of the rank
    pass   



