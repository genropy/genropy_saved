_fetchItems: function(	/* Object */ keywordArgs, 
						/* Function */ findCallback, 
						/* Function */ errorCallback){
	//	summary: 
	//		See dojo.data.util.simpleFetch.fetch()
	var self = this;
	var filter = function(requestArgs, arrayOfItems){
		var items = [];
		if(requestArgs.query){
			var ignoreCase = requestArgs.queryOptions ? requestArgs.queryOptions.ignoreCase : false; 

			//See if there are any string values that can be regexp parsed first to avoid multiple regexp gens on the
			//same value for each item examined.  Much more efficient.
			var regexpList = {};
			for(var key in requestArgs.query){
				var value = requestArgs.query[key];
				if(typeof value === "string"){
					regexpList[key] = dojo.data.util.filter.patternToRegExp(value, ignoreCase);
				}
			}

			for(var i = 0; i < arrayOfItems.length; ++i){
				var match = true;
				var candidateItem = arrayOfItems[i];
				if(candidateItem === null){
					match = false;
				}else{
					for(var key in requestArgs.query) {
						var value = requestArgs.query[key];
						if (!self._containsValue(candidateItem, key, value, regexpList[key])){
							match = false;
						}
					}
				}
				if(match){
					items.push(candidateItem);
				}
			}
			findCallback(items, requestArgs);
		}else{
			// We want a copy to pass back in case the parent wishes to sort the array. 
			// We shouldn't allow resort of the internal list, so that multiple callers 
			// can get lists and sort without affecting each other.  We also need to
			// filter out any null values that have been left as a result of deleteItem()
			// calls in ItemFileWriteStore.
			for(var i = 0; i < arrayOfItems.length; ++i){
				var item = arrayOfItems[i];
				if(item !== null){
					items.push(item);
				}
			}
			findCallback(items, requestArgs);
		}
	};

	if(this._loadFinished){
		filter(keywordArgs, this._getItemsArray(keywordArgs.queryOptions));
	}else{

		if(this._jsonFileUrl){
			//If fetches come in before the loading has finished, but while
			//a load is in progress, we have to defer the fetching to be 
			//invoked in the callback.
			if(this._loadInProgress){
				this._queuedFetches.push({args: keywordArgs, filter: filter});
			}else{
				this._loadInProgress = true;
				var getArgs = {
						url: self._jsonFileUrl, 
						handleAs: "json-comment-optional"
					};
				var getHandler = dojo.xhrGet(getArgs);
				getHandler.addCallback(function(data){
					try{
						self._getItemsFromLoadedData(data);
						self._loadFinished = true;
						self._loadInProgress = false;
						
						filter(keywordArgs, self._getItemsArray(keywordArgs.queryOptions));
						self._handleQueuedFetches();
					}catch(e){
						self._loadFinished = true;
						self._loadInProgress = false;
						errorCallback(e, keywordArgs);
					}
				});
				getHandler.addErrback(function(error){
					self._loadInProgress = false;
					errorCallback(error, keywordArgs);
				});
			}
		}else if(this._jsonData){
			try{
				this._loadFinished = true;
				this._getItemsFromLoadedData(this._jsonData);
				this._jsonData = null;
				filter(keywordArgs, this._getItemsArray(keywordArgs.queryOptions));
			}catch(e){
				errorCallback(e, keywordArgs);
			}
		}else{
			errorCallback(new Error("dojo.data.ItemFileReadStore: No JSON source data was provided as either URL or a nested Javascript object."), keywordArgs);
		}
	}
},