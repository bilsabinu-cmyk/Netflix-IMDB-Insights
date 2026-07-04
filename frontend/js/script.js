const API = "http://127.0.0.1:5000";

async function loadHomeData() {

    try {

        const response = await fetch(`${API}/dashboard`);
        const data = await response.json();

        document.getElementById("titles").textContent =
            data["Total Titles"];

        document.getElementById("movies").textContent =
            data["Movies"];

        document.getElementById("shows").textContent =
            data["TV Shows"];

        document.getElementById("positive").textContent =
            data["Positive Reviews"];

        const ctx = document
            .getElementById("typeChart")
            .getContext("2d");

        new Chart(ctx, {

            type: "doughnut",

            data: {

                labels: ["Movies", "TV Shows"],

                datasets: [{

                    data: [
                        data["Movies"],
                        data["TV Shows"]
                    ],

                    backgroundColor: [
                        "#FF3D00",
                        "#FAFAFA"
                    ],

                    borderColor: "#0A0A0A",

                    borderWidth: 4,

                    hoverOffset: 18

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "68%",

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            color: "#FAFAFA",

                            padding: 20,

                            font: {

                                family: "Inter",

                                size: 14,

                                weight: "600"

                            }

                        }

                    },

                    title: {

                        display: true,

                        text: "Movies vs TV Shows",

                        color: "#FAFAFA",

                        font: {

                            family: "Inter Tight",

                            size: 22,

                            weight: "700"

                        },

                        padding: {

                            bottom: 20

                        }

                    }

                }

            }

        });

    }

    catch (error) {

        console.error("Dashboard Error:", error);

        document.getElementById("titles").textContent = "--";
        document.getElementById("movies").textContent = "--";
        document.getElementById("shows").textContent = "--";
        document.getElementById("positive").textContent = "--";

    }

}

window.addEventListener("DOMContentLoaded", loadHomeData);