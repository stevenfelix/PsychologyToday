##
# Steven Felix
# February 15, 2017
# Description:  This codes analyses the profiles of therapists scraped from therapists.psychologytoday.com
##

# loading packages and data -----------------------------------------------

if (!require(tm)) install.packages("tm"); require(tm)
if (!require(wordcloud)) install.packages("wordcloud"); require(wordcloud)
#library(car)
library(psych)
library(effects)
#library("RSiteCatalyst")
library("RTextTools") #Loads many packages useful for text mining

rm(list = ls())


setwd('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/')
data <- read.table('data/psychologytoday2017-02-17.txt', sep = '\t', header = TRUE, stringsAsFactors = FALSE)
View(data)

table(data$title)
data <- data[data$title != 'treatment facility',]
# Dummy coding treatment approaches ---------------------------------------

# this could be more sophisticarted distinction between who is and who isn't CBT
ind <- grep(pattern = 'Cognitive Behavioral', x = data$treatmentorientation)
data$cbt <- 0
data$cbt[ind] <- 1
data$cbt <- factor(data$cbt, levels = c(0,1), labels = c('NoCBT','CBT'))

ind <- grep(pattern = 'Psychodynamic', x = data$treatmentorientation)
ind1 <- grep(pattern = 'Psychoanalytic', x = data$treatmentorientation)
ind <- c(ind,ind1)
ind <- unique(ind)

data$psychodynamic <- 0
data$psychodynamic[ind] <- 1
data$psychodynamic <- factor(data$psychodynamic, levels = c(0,1), labels = c('NoPD','PD'))
head(data$psychodynamic)

table(data$psychodynamic,data$cbt)

modlm <- lm(issuesnum ~ cbt + psychodynamic, data=data)
summary(modlm)
plot(allEffects(modlm))


vars <- c('issuesnum','cbt','psychodynamic')
data2 <- data[complete.cases(data[,vars]), vars]
tab1 <- as.table(by(data2$issuesnum, INDICES = list(data2$cbt,data2$psychodynamic), mean), dnn = c('num','blah'))

barplot(height = tab1, beside = TRUE, legend.text = TRUE)
mod <- aov(formula = issuesnum ~ cbt*psychodynamic, data = data2)
summary(mod)
TukeyHSD(mod)


interaction.plot(data2$cbt, data2$psychodynamic, data2$issuesnum, type = 'b', col = rainbow(5)[1:2], 
                 xlab = 'CBT', ylab = 'Number Issues Treated', legend = FALSE)
legend("bottomright", legend = c('Not Psychodynamic','Psychodynamic'), lty = 1, col = rainbow(5)[1:2], cex = 0.6)
## against my intuitions -- there are two main effects -- CBT --> more issues, psychodyanm --> more issues
## also, CBT only > Psychodynamic only

interaction.plot(data$cbt, data$psychodynamic, data$issuesnum, ylab = "Attractiveness", xlab = "Gender", 
                 type = "b", pch = 19, lty = 1, legend = FALSE, col = rainbow(5)[1:2], na.rm=TRUE)
legend("bottomright", legend = c("None", "2 drinks", "4 drinks"), lty = 1, col = rainbow(5)[1:3], cex = 0.6)


# descriptives ------------------------------------------------------------
names(data)
numericVars <- c('years','fee','issuesnum','mentalhealthnum','treatmentorientationnum')
describe(data[,numericVars])
op = par(mfrow = c(3,2))
for(i in numericVars){
    hist(data[,c(i)], main = paste(i), freq = FALSE)
}
par(op)
## numbre of issues and tratment orientation strongly skewed right

describe(data$treatmentorientationnum)
quantile(data$treatmentorientationnum, probs = c(.25,.75), na.rm = TRUE)
## interquartile range is 6 (4 - 10)

describe(data$issuesnum) # M = 15.7, med = 14
quantile(data$issuesnum, probs = c(.25,.75), na.rm = TRUE)
## interquartile range is 10 (10 - 20)

pairs(~years+fee+issuesnum+treatmentorientationnum,data=data, 
      main="Simple Scatterplot Matrix")

corr.test(data[,numericVars])
# little relationship between years and fee
# treatment orientation linked to issues (r = .48)
# issues links to both oreitnation and mental health (r = .45)

# people who say they treat lots of issues, also have lots of treatment orientations
mod <- lm(issuesnum ~ treatmentorientationnum, data = data)
summary(mod)
# almost 1:1 -- for every treatment orientation added, another issue treated
plot(issuesnum ~ treatmentorientationnum, data = data)
abline(a = mod$coefficients[1], b = mod$coefficients[2])

data$profile[sample(1:nrow(data), 1)]
data[sample(1:nrow(data), 5), c('name','degrees','title','city')]
names(data)
# Word cloud for all data  --------------------------------------------------

profiles <- data$profile
allprofiles <- paste(profiles, collapse='')

# convert the books to corpora with the tm package
corpus <- Corpus(VectorSource(allprofiles))

# create term-document matrix
tdm <- TermDocumentMatrix(corpus,control = list(
  removePunctuation = TRUE, # remove punctuation
  stopwords = TRUE, # remove stopwords (high frequency)
  tolower = TRUE, # make all lower case
  removeNumbers = TRUE, # remove numbers
  bounds = list(local=c(10,Inf)))) # only include cases with at least two occurences
tdm <- as.matrix(tdm)

# save commonality cloud to PDF
pdf("allprofiles_commonality_cloud.pdf", width=8, height=8)
commonality.cloud(tdm, random.order=FALSE, colors = brewer.pal(8, "Dark2"), max.words=250)
dev.off()


# Word cloud, CBT vs non-CBT --------------------------------------



profilesCBT <- paste(data$profile[data$cbt == 'CBT'], collapse ='')
profilesNonCBT <- paste(data$profile[data$cbt == 'NoCBT'], collapse ='')
profiles <- c(profilesCBT,profilesNonCBT)

# convert the books to corpora with the tm package
corpus <- Corpus(VectorSource(profiles))

# create term-document matrix
tdm <- TermDocumentMatrix(corpus,control = list(
  removePunctuation = TRUE, # remove punctuation
  stopwords = TRUE, # remove stopwords (high frequency)
  tolower = TRUE, # make all lower case
  removeNumbers = TRUE, # remove numbers
  bounds = list(local=c(300,Inf)))) # only include cases with at least two occurences
tdm <- as.matrix(tdm)

# save commonality cloud to PDF
pdf("visualizations/CBT_commonality_cloud_50.pdf", width=8, height=8)
commonality.cloud(tdm, random.order=FALSE, colors = brewer.pal(8, "Dark2"), max.words=250)
dev.off()

# save comparison cloud to PDF
pdf("visualizations/CBT_comparison_cloud_50.pdf", width=8, height=8)
comparison.cloud(tdm,  random.order=FALSE, colors = c("red","blue"), max.words=250)
dev.off()


# Word Cloud: psychologists vs social workers -----------------------------



data$title2 <- recode(data$title, recodes = "'psychologist' = 'psychologist'; 'clinical social work/therapist' = 
                      'clinical social work/therapist'; 'licensed professional counselor' = 'counselor'; 'counselor' = 'counselor';
                      'psychiatrist' = 'psychiatrist'; else = 'other'")
table(data$title2)
profilesMSW <- paste(data$profile[data$title2 == 'clinical social work/therapist'], collapse ='')
profilesCounselor <- paste(data$profile[data$title2 == 'counselor'], collapse ='')
profilesShrink <- paste(data$profile[data$title2 == 'psychiatrist'], collapse ='')
profilesPsych <- paste(data$profile[data$title2 == 'psychologist'], collapse ='')
profilesOther <- paste(data$profile[data$title2 == 'other'], collapse ='')

profiles <- c(profilesMSW,profilesCounselor,profilesShrink,profilesPsych,profilesOther)

# convert the books to corpora with the tm package
corpus <- Corpus(VectorSource(profiles))

# create term-document matrix
tdm <- TermDocumentMatrix(corpus,control = list(
  removePunctuation = TRUE, # remove punctuation
  stopwords = TRUE, # remove stopwords (high frequency)
  tolower = TRUE, # make all lower case
  removeNumbers = TRUE, # remove numbers
  bounds = list(local=c(2,Inf)))) # only include cases with at least two occurences
tdm <- as.matrix(tdm)

# save commonality cloud to PDF
pdf("commonality_cloud.pdf", width=8, height=8)
commonality.cloud(tdm, random.order=FALSE, colors = brewer.pal(8, "Dark2"), max.words=250)
dev.off()

# save comparison cloud to PDF
pdf("comparison_cloud.pdf", width=8, height=8)
comparison.cloud(tdm,  random.order=FALSE, colors = c("red","blue", "green","purple","orange"), max.words=250)
dev.off()

## LOTS OF ERRORS ON THE COMPARISON -- LOTS OF PSYCHIATRIST WORDS, FEWER ONES FOR PSYCHOLOGISTS AND MSWs.




# Research questions: 
# - are there certain 'types' of therapists? how do therapists cluster?
#
#
# - cluster analysis based on treatment approaches
#
#
#
#


# co-occurence table ------------------------------------------------------

# put books together
books <- data$treatmentorientation

# convert the books to corpora with the tm package
corpus <- Corpus(VectorSource(books))

# create term-doument matrix
tdm <- TermDocumentMatrix(corpus,control = list(
  removePunctuation = TRUE, # remove punctuation
  stopwords = TRUE, # remove stopwords (high frequency)
  tolower = TRUE, # make all lower case
  removeNumbers = TRUE, # remove numbers
  bounds = list(local=c(10,Inf)))) # only include cases with at least two occurences
tdm <- as.matrix(tdm)


dtm <- create_matrix(data$treatmentorientation, 
                     stemWords=TRUE, 
                     removeStopwords=FALSE, 
                     minWordLength=3,
                     removePunctuation= TRUE)
findFreqTerms(dtm, lowfreq=400)

#I think there are 5 main topics: Data Science, Web Analytics, R, Julia, Wordpress
kmeans5<- kmeans(dtm, 5)

#Merge cluster assignment back to keywords
kw_with_cluster <- as.data.frame(cbind(data$treatmentorientation, kmeans5$cluster))
names(kw_with_cluster) <- c("treatmentorientation", "kmeans5")

#Make df for each cluster result, quickly "eyeball" results
cluster1 <- subset(kw_with_cluster, subset=kmeans5 == 1)
cluster2 <- subset(kw_with_cluster, subset=kmeans5 == 2)
cluster3 <- subset(kw_with_cluster, subset=kmeans5 == 3)
cluster4 <- subset(kw_with_cluster, subset=kmeans5 == 4)
cluster5 <- subset(kw_with_cluster, subset=kmeans5 == 5)

dim(cluster1)
View(cluster1)

dim(cluster2)
View(cluster2)

dim(cluster3)
View(cluster3)

#accumulator for cost results
cost_df <- data.frame()

#run kmeans for all clusters up to 100
for(i in 1:100){
  #Run kmeans for each level of i, allowing up to 100 iterations for convergence
  kmeans<- kmeans(x=dtm, centers=i, iter.max=100)
  
  #Combine cluster number and cost together, write to df
  cost_df<- rbind(cost_df, cbind(i, kmeans$tot.withinss))
  
}
names(cost_df) <- c("cluster", "cost")

orientation <- tolower(paste(data$treatmentorientation, collapse=', '))
orientationVec <- as.vector(strsplit(orientation, ', '))
frequencies <- as.data.frame(table(orientationVec))
frequencies

#mind-body
#mindfulness
#mentalization
#marital / couples / family / relationship
#jungian
#family systems
#holisitic
#exposure
# emotionally focused
# emdr
# eft / emotional freedom technique / tapping
# art / drama
#dbt / dialectical 
# cbt / cognitive behavioral
# coaching
# humanistic / person centered / client centered /rogerian
#mind-body / body- mind
# attachment
# ACT / acceptance / commitment
# sex addition
# relaxation
# relapse / twelve step / addiction
# psychodynamic / psychoanalytic, psychoanalysis
# solution-focused
# trauma / 
#strength(s) - based
frequencies[[1][500:length(frequencies[[1]])]
