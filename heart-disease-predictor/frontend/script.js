document.addEventListener('DOMContentLoaded', () => {
    // Wizard Elements
    const formSteps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const progressBar = document.getElementById('progress-bar');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    const form = document.getElementById('prediction-form');
    
    // Result Elements
    const resultCard = document.getElementById('result-card');
    const closeBtn = document.getElementById('close-btn');
    const scoreCircle = document.getElementById('score-circle');
    const scoreText = document.getElementById('score-text');
    const resultTitle = document.getElementById('result-title');
    const resultDesc = document.getElementById('result-desc');
    const factorsList = document.getElementById('factors-list');
    
    let currentStep = 0;

    // Initialize wizard
    updateWizard();

    nextBtn.addEventListener('click', () => {
        // Simple HTML5 validation for the current step
        const currentInputs = formSteps[currentStep].querySelectorAll('input[required]');
        let isValid = true;
        currentInputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                isValid = false;
            }
        });

        if (isValid) {
            currentStep++;
            updateWizard();
        }
    });

    prevBtn.addEventListener('click', () => {
        currentStep--;
        updateWizard();
    });

    function updateWizard() {
        // Show/hide steps
        formSteps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Update indicators
        stepIndicators.forEach((indicator, index) => {
            if (index <= currentStep) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });

        // Update progress bar width
        const progress = ((currentStep + 1) / formSteps.length) * 100;
        progressBar.style.width = `${progress}%`;

        // Update buttons
        if (currentStep === 0) {
            prevBtn.disabled = true;
        } else {
            prevBtn.disabled = false;
        }

        if (currentStep === formSteps.length - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btnText = submitBtn.querySelector('span');
        const loader = document.getElementById('btn-loader');
        
        // Show loading state
        btnText.style.display = 'none';
        loader.style.display = 'block';
        submitBtn.disabled = true;

        // Gather form data
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = parseFloat(value);
        }

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            showResult(result);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the prediction server. Please ensure the backend is running.');
        } finally {
            // Restore button state
            btnText.style.display = 'block';
            loader.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    closeBtn.addEventListener('click', () => {
        resultCard.classList.add('hidden');
    });

    function showResult(result) {
        // probability is between 0 and 1
        const prob = Math.round(result.probability * 100);
        
        // Update circle animation and text
        setTimeout(() => {
            scoreCircle.setAttribute('stroke-dasharray', `${prob}, 100`);
            scoreText.textContent = `${prob}%`;
        }, 100);

        if (result.prediction === 1) {
            scoreCircle.setAttribute('stroke', '#ff3333');
            resultTitle.textContent = 'High Risk Detected';
            resultTitle.style.color = '#ff3333';
            resultDesc.textContent = 'The AI model indicates a high probability of heart disease.';
        } else {
            scoreCircle.setAttribute('stroke', '#4CAF50');
            resultTitle.textContent = 'Low Risk Detected';
            resultTitle.style.color = '#4CAF50';
            resultDesc.textContent = 'The AI model indicates a low probability of heart disease.';
        }

        // Render Top Features
        factorsList.innerHTML = '';
        if (result.top_features && result.top_features.length > 0) {
            result.top_features.forEach(factor => {
                const li = document.createElement('li');
                const name = document.createElement('span');
                name.textContent = factor.feature;
                const val = document.createElement('span');
                val.className = 'val';
                
                // Display whether the contribution increased or decreased risk
                if (factor.value > 0) {
                    val.textContent = '↑ Increased Risk';
                    val.style.color = '#ff3333';
                } else {
                    val.textContent = '↓ Decreased Risk';
                    val.style.color = '#4CAF50';
                }
                
                li.appendChild(name);
                li.appendChild(val);
                factorsList.appendChild(li);
            });
        }

        resultCard.classList.remove('hidden');
    }
});
