from plotly.offline import plot,iplot
import plotly_express as px
import pandas as pd


class plot_engagement:
	'''
		plot_engagement receives a dataframe and name of politician
	'''
	def __init__(self,tweet_df,name):
		assert isinstance(tweet_df,dict), "tweet_df must be a dictionary"
		assert isinstance(name,str), "name must be string type"
		if not name in tweet_df: raise ValueError("that politician does not exist in dataframe")
		assert len(name)>0, "empty string"
		assert len(tweet_df)>0, "empty dataframe"
		for val in tweet_df: assert isinstance(tweet_df[val],pd.DataFrame), "values in dictionary must be dataframe"

		#attributes 
		self.tweet_df = tweet_df
		self.name = name
		self.this_person = self.tweet_df[self.name]
		self.real_name = self.this_person['User Name'][0]
		self.friend_count = self.this_person['Friend Count']
		self.length = max(self.this_person.index)

		#some columns in dataframe
		self.polarity = self.this_person['Polarity']
		self.favorite = self.this_person['Favorites']
		self.retweets = self.this_person['Retweets']
		self.subjectivity = self.this_person['Subjectivity']		

		self.this_person['yr-month'] = pd.to_datetime((self.this_person['Date Created'])).dt.strftime('%Y-%b %A') #formatting date
		self.daily = self.this_person.groupby('yr-month')

	def __repr__(self):
		'''
			returns instance data location
		'''
		return "plot_engagement object at address "+hex(id(self))

	def calc_engagement(self):
		'''
			Calculates engagement scores for a politician
		'''
		self.this_person['Engagement'] = ((2*self.this_person['Retweets'] + self.this_person['Favorites'])**2)

		return

	def create_plotly_df(self):
		self.calc_engagement()

		#finds locations of max engagement
		max_locs = self.this_person.groupby('Date Created')['Engagement'].idxmax()

		#new dataframe created for use with plotly express
		plot_df = pd.DataFrame(pd.Series(self.this_person.loc[max_locs]['Date Created'],name="Date"))
		plot_df['Retweets'] = self.this_person.loc[max_locs]['Retweets']
		plot_df['Favorites'] = self.this_person.loc[max_locs]['Favorites']
		plot_df['Engagement'] = self.this_person.loc[max_locs]['Engagement']
		plot_df['Polarity'] = self.this_person.loc[max_locs]['Polarity']
		plot_df['Subjectivity'] = self.this_person.loc[max_locs]['Subjectivity']
		plot_df['Tweet'] = self.this_person.loc[max_locs]['Tweet']
		
		#fix hovertext width by reformatting
		formatted = []
		for tweet in self.this_person['Tweet']:
			temp = self.format_hovertext(tweet,10)
			formatted.append(temp)
		self.this_person['Formatted Tweet'] = pd.DataFrame(formatted)

		#creates new column in plot_df to formatted tweet
		plot_df['Formatted Tweet'] = self.this_person.loc[max_locs]['Formatted Tweet']

		return plot_df

	def bubble_chart(self):
		'''
			bubble_chart plots engagement scatter plot for a politician
		'''
		#gathers and formates plotly dataframe
		plot_df = self.create_plotly_df()

		#plots bubble chart of engagement
		p1 = px.scatter(plot_df,x="Date", y="Polarity",
					size='Engagement',hover_data=["Formatted Tweet","Retweets","Favorites"],
					opacity=.95,size_max=70,title=self.real_name+' - Engagement vs. Polarity',
					color="Polarity",labels=({"Formatted Tweet":"Tweet"}),
					color_continuous_scale=['red','rgb(220,220,220)','rgb(0,191,255)'])
		#py.plot(p1)	#for online plotting	
		plot(p1)

		return

	def format_hovertext(self,string,n):
		'''
			Receives: tweet (string) and integer n that dictates how many words to place line breaks
			Returns: returns the formatted tweet 

			inserts <br> tags (line breaks) in tweet to format hovertext in scatter plot
		'''
		split=string.split()
		i=1
		result = ''
		while (i * n) < len(split):
			result = result +' '.join(split[(i-1)*n:i *n]) + '<br>'
			i+=1
		result +=' '.join(split[(i-1)*n:])

		return result

#to load tweet_df so we don't have to rescrape every time
if __name__ == '__main__':


	tweet_df=dict()

	with open('twitter_handles.txt') as f:
		polit_list = f.read().rstrip('\n').split('\n')
	for i in polit_list:
		tweet_df[i] = pd.read_csv(i + '_tweets.csv')
