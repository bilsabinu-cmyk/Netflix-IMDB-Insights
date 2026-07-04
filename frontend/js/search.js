const API = "http://127.0.0.1:5000";

async function searchMovie() {

    const movie = document.getElementById("movie").value.trim();

    const result = document.getElementById("result");

    if (movie === "") {

        result.innerHTML = `

        <div class="movie-card">

            <h2 style="color:#FF3D00;">Search Required</h2>

            <p>Please enter a movie or TV show name.</p>

        </div>

        `;

        return;

    }

    result.innerHTML = `

    <div class="movie-card">

        <h2>Searching...</h2>

        <p>Please wait while we fetch the data.</p>

    </div>

    `;

    try {

        const response = await fetch(

            API + "/search/" + encodeURIComponent(movie)

        );

        const data = await response.json();

        result.innerHTML = "";

        if (data.message) {

            result.innerHTML = `

            <div class="movie-card">

                <h2 style="color:#FF3D00;">

                    ${data.message}

                </h2>

                <p>

                    Try another Netflix title.

                </p>

            </div>

            `;

            return;

        }

        data.forEach(item => {

            result.innerHTML += `

            <div class="movie-card">

                <small>

                    NETFLIX • IMDb DATASET

                </small>

                <div class="accent-bar"></div>

                <h2>

                    ${item.title}

                </h2>

                <p>

                    <strong>Type:</strong>

                    ${item.type}

                </p>

                <p>

                    <strong>Genre:</strong>

                    ${item.listed_in}

                </p>

                <p>

                    <strong>Country:</strong>

                    ${item.country}

                </p>

                <p>

                    <strong>Release Year:</strong>

                    ${item.release_year}

                </p>

                <p>

                    <strong>Rating:</strong>

                    ${item.rating}

                </p>

                <p>

                    <strong>Sentiment:</strong>

                    <span style="color:#FF3D00;font-weight:700;">

                        ${item.sentiment}

                    </span>

                </p>

                <hr style="margin:20px 0;border:1px solid #262626;">

                <p>

                    ${item.description}

                </p>

            </div>

            `;

        });

    }

    catch (error) {

        console.error(error);

        result.innerHTML = `

        <div class="movie-card">

            <h2 style="color:#FF3D00;">

                Connection Failed

            </h2>

            <p>

                Unable to connect to the Flask backend.

            </p>

            <p>

                Make sure your backend is running on

                <strong>http://127.0.0.1:5000</strong>

            </p>

        </div>

        `;

    }

}

document.getElementById("movie").addEventListener("keypress", function(event) {

    if (event.key === "Enter") {

        searchMovie();

    }

});