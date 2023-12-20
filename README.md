### Mask-Catcher
#### words
- **stopwords.txt:** Publicly available list of stopwords in Chinese.
- **stopwords_profile.txt:** Additional stopwords based on the characteristics of descriptions.
- **stopwords_comm.txt:** Additional stopwords based on the characteristics of user reviews.
- **reversed.txt:** Reserved words added for jieba.
- **row_themewords.txt:** Words that describe app functionalities added for topic words list.
#### spider
- **appStoreSpider.py:** Crawler tool for the App Store to collect metadata, including descriptions, user reviews, inter-app recommendation relationships, categories, ratings, and other information for target apps.
#### preprocess
- **preClean_profile.py:** Preprocessing of descriptions, including filtering out redundant sentences, tokenizing and removing stopwords.
- **preClean_comm.py:** Preprocessing of user reviews, including filtering out redundant sentences, tokenizing and removing stopwords.
#### filter0_resource
- **resource.py:** The core code of Filter 0 (mentioned in subsection 3.3) using regular rules to filter out apps that may be pirate resource providers.
#### filter1_sim
- **modelLDA_profile.py:** The functionality extraction part of Filter 1, extracting the claimed functionalities of the app from the description using LDA.
- **modelLDA_comm.py:** The functionality extraction part of Filter 1, extracting the hidden functionalities of the app from the user reviews using LDA.
- **modelW2V.py:** Train and use Word2Vec model to map the representative words to 64-dimensional vectors.
- **discover_sim.py:** The suspicious app discovery part of Filter 1, calculating the cosine similarities between claimed and hidden functionalities vectors and geting the label.
#### filter2_graph
- **modelRFC.py:** Train and use Random Forest Classifier to get the claimed categories set from descriptions.
- **get_graph.py:** Construct the graph GCN model required from the inter-app recommendation relationships.
- **modelGCN.py:** Train and use GCN model to get the hidden categories set from user reviews.
- **discover_graph.py:** The suspicious app discovery part of Filter 2, checking if there is an overlap between claimed and hidden sets and geting the label.
#### filter3_reverse
- **get_ipa.py:** Crawler tool for ipa files using *ipatool*.
- **ipa_process.py:** Extract the binary files from ipa files, disassemble and generate binExport files using *IDA Pro*
- **get_i64.idc:** idc script for disassembling in *IPA Pro*.
- **get_binExport.idc:** idc script for generating binExport files in *IPA Pro*.
- **get_sim_bindiff.py:** Calculate the code similarity between the suspicious apps and the Mask App family representatives using the *bindiff* plugin.
- **identify_sim.py:** The Mask App identification part of Filter 3, using Random Forest Classifier to identify Mask Apps.
