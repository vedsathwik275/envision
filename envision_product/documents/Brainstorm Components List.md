Ok lets think through this

Some of the features that we need to work on:

1. OTM data importing the OTM data for rate and query. We're going to do that via REST API. We have to input the data for our requirements, the contract rates, the req, and then format the data needs to be in, and then we import the spot API data from OTM now Spot API. That's a tool as well that we can build.
2. Export the Gmail attachment into a Drive for carrier performance and the same for tender performance. Those two, we can also build.
3. What we could do honestly is have a tool that acts as an all-in-one place where you can just go run it or call or like call an API right? So we go call the API, and it does everything for us like that. This tool does is when you call the API right it gets the data then it asks for the data then it exports the Gmail attachment that we get into the Google Drive for carrier performance and tender performance. 
4. We can also have the tool for the Spot API to get the data from the Spot API and then input carrier performance neural network model. 
5. Google Drive storage for prompts, preferences, recommendations, and other structures for Rag. I don't know if we still need to do a Rag agent
	1. CrawlAI Rag Tool + S3 Bucket
6. Some of the tools we need to do is the S3 bucket tool, the read and write to read and write S3 bucket tool definitely. 
7. The main thing now is to build the recommendations algorithm that's the main tool that we need to build.

Tools we need to build
1. Tool that imports OTM data for rate and query based on the contract rates, the RIQ, and the format the data needs to be in
2. Tool that imports SPOT data from the OTMNow Spot API
3. Tool that exports the Gmail attachments for carrier and tender performance into Google Drive or S3 bucket
4. CrawlAI Rag Tool for the ChatBot component
5. S3 read and write tool. All in one, reads any document needed, and writes to and updates any document needed. 
6. Recommendation algorithm for the best rate given lane and timing

One thing to keep in mind is that we need **clear naming conventions**