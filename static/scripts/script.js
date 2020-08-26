//need to create function for verifying passwords match
//create function for displaying hidden contents
//create function to count remaining characters left in text box
function displayArea(value)
{

	var x = document.getElementById(value); //get the item via their id

        if(x.style.display === "none")	//if they are hidden, show display
         {
               x.style.display = "block";
         }
         else	//if they are displayed , hide.
         {
               x.style.display = "none";
         }
        

}


  maxL=500;
  var bName = navigator.appName;
  function taLimit(taObj) {
        if (taObj.value.length==maxL) return false;
        return true;
  }
  
  function taCount(taObj,Cnt) { 
        objCnt=createObject(Cnt);
        objVal=taObj.value;
        if (objVal.length>maxL) objVal=objVal.substring(0,maxL);
        if (objCnt) {
              if(bName == "Netscape"){	
                    objCnt.textContent=maxL-objVal.length;}
              else{objCnt.innerText=maxL-objVal.length;}
        }
        return true;
  }
  function createObject(objId) {
        if (document.getElementById) return document.getElementById(objId);
        else if (document.layers) return eval("document." + objId);
        else if (document.all) return eval("document.all." + objId);
        else return eval("document." + objId);
  }





  function validateRegForm() {

      var passwrd = document.forms["regform"]["passwrdcreate"].value;
      var passwrdconfirm = document.forms["regform"]["passwrdconfirm"].value;

      if (passwrd != passwrdconfirm) {
            var error = document.getElementById("errorMessage")
            error.innerHTML = "*Passwords don't match, try again!"
            error.style = "color: red;"
            document.forms["regform"]["passwrdconfirm"].value = ""
            document.forms["regform"]["passwrdcreate"].value = ""
            return false;
            
      }

  }
  
