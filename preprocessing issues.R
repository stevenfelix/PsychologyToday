##
# Steven Felix
# March 21, 2017
# Description:  This code preprocesses my raw datas so that I have dummy codes of the mental health variables
##
 
# loading packages and data -----------------------------------------------

library(vegan)
rm(list = ls())


setwd('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/')
data <- read.table('data/psychologytoday2017-02-17.txt', sep = '\t', header = TRUE, stringsAsFactors = FALSE)
data <- data[data$title != 'treatment facility',]
View(data)

names(data)

head(data$issues)


# Preprocessing -----------------------------------------------------------

# create list of all unique "issues"
allissues.str <- paste(data$issues, collapse =', ')
allissues.vec <- strsplit(x = allissues.str, split = ', ')[[1]]
issues.unique <- unique(allissues.vec)

# find a reasonable cut off to include only those with a reasonable frequency
sort(table(allissues.vec)) # couple therapy = 6, CHornic Illness = 19, let's use a cut off of 20
issues.xtab <- sort(table(allissues.vec)[table(allissues.vec) >= 19])
issues.xtab <- issues.xtab[!names(issues.xtab) == ""]
barplot(issues.xtab)

# creaty dummy variables for desired variables

issues <- names(issues.xtab)
data.issues <- data[,c('X','name','issues')]

for(issue in issues){
  dummy <- as.numeric(grepl(pattern = issue, x = data$issues))
  data.issues[,issue] <- dummy
}

# Test correctness
View(data.issues)
table(data.issues$'Chronic Illness')
issues.xtab['Chronic Illness']
table(data.issues$'Self Esteem')
issues.xtab['Self Esteem']


# Distance matrix ---------------------------------------------------------
names(data.issues)
View(data.issues[,4:75])

dist.mat.binary<-dist(data.issues[,4:75],method = 'binary')
dist.mat.jaccard<-vegdist(data.issues[,4:75],method="jaccard", binary = T)

clust.res<-hclust(dist.mat.binary)
plot(clust.res)
