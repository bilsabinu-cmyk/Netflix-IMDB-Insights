const API = "";

async function loadGenreChart(){

const res = await fetch(API+"/genres");

const data = await res.json();

new Chart(

document.getElementById("genreChart"),

{

type:"bar",

data:{

labels:Object.keys(data),

datasets:[{

label:"Genres",

data:Object.values(data)

}]

}

}

);

}

async function loadCountryChart(){

const res = await fetch(API+"/countries");

const data = await res.json();

new Chart(

document.getElementById("countryChart"),

{

type:"bar",

data:{

labels:Object.keys(data),

datasets:[{

label:"Countries",

data:Object.values(data)

}]

}

}

);

}

async function loadYearChart(){

const res = await fetch(API+"/years");

const data = await res.json();

new Chart(

document.getElementById("yearChart"),

{

type:"line",

data:{

labels:Object.keys(data),

datasets:[{

label:"Release Year",

data:Object.values(data),

fill:false

}]

}

}

);

}

async function loadSentimentChart(){

const res = await fetch(API+"/sentiment");

const data = await res.json();

new Chart(

document.getElementById("sentimentChart"),

{

type:"doughnut",

data:{

labels:Object.keys(data),

datasets:[{

data:Object.values(data)

}]

}

}

);

}

window.onload=function(){

loadGenreChart();

loadCountryChart();

loadYearChart();

loadSentimentChart();

};