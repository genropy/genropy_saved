function toPermalink(string){ 
		 //var permalink = string.replace(/ /g,'_');
		 //console.log('permalinko');
		 var permalink=string.replace(/[^a-z0-9]+/gi, '-').replace(/^-*|-*$/g, '');
		 return permalink;
}