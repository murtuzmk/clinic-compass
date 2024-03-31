const express = require('express');
const app = express();
const port = 4000;

// Serve static files (e.g., HTML, CSS, JavaScript) from the 'public' directory
app.use(express.static('public'));

app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`);
});
