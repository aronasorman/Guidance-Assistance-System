// JavaScript document

function compare()
{ 
    var a = document.getElementById("username").value;
    var b = document.getElementById("currpass").value;
    var c = document.getElementById("newpass").value;
    var d = document.getElementById("confirm").value;
    
    if(a.length == 0 || b.length == 0 || c.length == 0 || d.length == 0  )
    {
	alert("Please fill up all fields.");
    }	
    else
    {
	if(c.length < 7)
	{
	    alert("Password must be atleast 7 characters long");
	}	
	else if(c != d)
	{
	    alert("New Password does not match.");
	}
	else
	{
	    document.getElementById("username").value = "";
	    document.getElementById("currpass").value = "";
	    document.getElementById("newpass").value = "";
	    document.getElementById("confirm").value = "";
	    alert("Successfully changed your password.");
 	}
    }		
}

function change()
{
    //alert("Juan Dela Cruz");
    var x = document.getElementById("who").options(who.selectedIndex).value;
    
    if(x==1)
    {
	document.getElementById("counselor").innerHTML="Juan Dela Cruz";
    }
    else if(x==2)
    {
	document.getElementById("counselor").innerHTML="April Canlas";
    }	
    else if(x==3)
    {
	document.getElementById("counselor").innerHTML="Aron Asor";
    }
    else if(x==4)
    {
	document.getElementById("counselor").innerHTML="Anna Uy";
    }
    else if(x==5)
    {
	document.getElementById("counselor").innerHTML="Fredie Verayo";
    }
    
}

function change2()
{
    var x = $('select#category_drop option:selected').val();

    if(x==0)
    {
	document.getElementById("categories").innerHTML="General Mental Ability";
	$('div#notations #textarea').val('boohoo');
    }
    else if(x==1)
    {
	document.getElementById("categories").innerHTML="Academic History";
	$('div#notations #textarea').val('boohoo2');
    }	
    else if(x==2)
    {
	document.getElementById("categories").innerHTML="Family Relationship";
    }
    else if(x==3)
    {
	document.getElementById("categories").innerHTML="Personal/Emotional";
    }
    else if(x==4)
    {
	document.getElementById("categories").innerHTML="Peer Relationship";
    }
    else if(x==5)
    {
	document.getElementById("categories").innerHTML="Goals/Motivation";
    }
    else if(x==6)
    {
	document.getElementById("categories").innerHTML="Recommendation";
    }
 
}