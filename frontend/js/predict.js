const API = "";

async function predict() {

    const type = document.getElementById("type").value.trim();

    const country = document.getElementById("country").value.trim();

    const release_year = document.getElementById("release_year").value.trim();

    const rating = document.getElementById("rating").value.trim();

    const listed_in = document.getElementById("listed_in").value.trim();

    const output = document.getElementById("output");

    /* ===========================
          INPUT VALIDATION
    =========================== */

    if (
        type === "" ||
        country === "" ||
        release_year === "" ||
        rating === "" ||
        listed_in === ""
    ) {

        output.innerHTML = `

        <div class="movie-card">

            <h2 style="color:#FF3D00;">
                Missing Information
            </h2>

            <p>
                Please fill in all fields before making a prediction.
            </p>

        </div>

        `;

        return;

    }

    output.innerHTML = `

    <div class="movie-card">

        <h2>Predicting...</h2>

        <p>Please wait while the Machine Learning model processes your request.</p>

    </div>

    `;

    try {

        const response = await fetch(`${API}/predict`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                type,

                country,

                release_year: Number(release_year),

                rating,

                listed_in

            })

        });

        const data = await response.json();

        output.innerHTML = `

        <div class="movie-card">

            <small>

                MACHINE LEARNING RESULT

            </small>

            <div class="accent-bar"></div>

            <h2 style="color:#FF3D00;">

                ${data.Prediction}

            </h2>

            <p>

                <strong>Model Used:</strong>

                ${data.Model}

            </p>

            <hr style="margin:20px 0;border:1px solid #262626;">

            <p>

                This prediction is generated using the trained Machine Learning model based on the provided Netflix content features.

            </p>

        </div>

        `;

    }

    catch (error) {

        console.error(error);

        output.innerHTML = `

        <div class="movie-card">

            <h2 style="color:#FF3D00;">

                Prediction Failed

            </h2>

            <p>

                Unable to connect to the Flask backend.

            </p>

            <p>

                Ensure the backend server is running on
                <strong> </strong>

            </p>

        </div>

        `;

    }

}

document.addEventListener("keypress", function (event) {

    if (event.key === "Enter") {

        predict();

    }

});