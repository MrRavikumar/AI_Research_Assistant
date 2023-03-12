// const userRouter = require('./routes/user');
// const postRouter = require('./routes/post');
// const chatRouter = require('./routes/chat');
const {getJson} = require("serpapi")
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const app = express();

app.use(cors())
app.use(express.json())




app.post("/searchPapers", async (req,res)=>{
    console.log(req.body)
    let paperTitle = req.body 
    let paper = paperTitle["title"]
    console.log(paperTitle)
    const params = {
        q: paper,
        api_key: "9dd5f82a389fc1a27e83791f4e132b3b1abf27072713ee746ba36bb3c398928f"
      };
    
    // Show result as JSON
    const response = await getJson("google_scholar", params);
    // console.log(response["organic_results"])
    res.send(response["organic_results"])
    
})

app.listen(8000,()=>{
    console.log("Server is Up and Running")
})