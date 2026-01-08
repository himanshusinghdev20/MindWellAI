document.addEventListener('DOMContentLoaded', () => {
    const signinModal = document.getElementById('signin-modal');
    const signupModal = document.getElementById('signup-modal');
    const signinNavBtn = document.getElementById('signin-nav-btn');
    const signupNavBtn = document.getElementById('signup-nav-btn');
    const closeSignin = document.getElementById('close-signin');
    const closeSignup = document.getElementById('close-signup');
    const switchToSignup = document.getElementById('switch-to-signup');
    const switchToSignin = document.getElementById('switch-to-signin');
    const startConversationBtn = document.getElementById('start-conversation-btn');
    const learnMoreBtn = document.getElementById('learn-more-btn');

    signinNavBtn.addEventListener('click', () => {
        signinModal.classList.remove('hidden');
    });

    signupNavBtn.addEventListener('click', () => {
        signupModal.classList.remove('hidden');
    });

    closeSignin.addEventListener('click', () => {
        signinModal.classList.add('hidden');
    });

    closeSignup.addEventListener('click', () => {
        signupModal.classList.add('hidden');
    });

    switchToSignup.addEventListener('click', (e) => {
        e.preventDefault();
        signinModal.classList.add('hidden');
        signupModal.classList.remove('hidden');
    });

    switchToSignin.addEventListener('click', (e) => {
        e.preventDefault();
        signupModal.classList.add('hidden');
        signinModal.classList.remove('hidden');
    });

    signinModal.addEventListener('click', (e) => {
        if (e.target === signinModal) {
            signinModal.classList.add('hidden');
        }
    });

    signupModal.addEventListener('click', (e) => {
        if (e.target === signupModal) {
            signupModal.classList.add('hidden');
        }
    });

    startConversationBtn.addEventListener('click', () => {
        window.location.href = '/chat';
    });

    learnMoreBtn.addEventListener('click', () => {
        document.querySelector('.features').scrollIntoView({ behavior: 'smooth' });
    });

    document.getElementById('signin-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('signin-email').value;
        const password = document.getElementById('signin-password').value;

        try {
            const response = await fetch('/auth/signin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                window.location.href = '/chat';
            } else {
                alert(data.error || 'Sign in failed');
            }
        } catch (error) {
            alert('An error occurred. Please try again.');
        }
    });

    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        try {
            const response = await fetch('/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                window.location.href = '/chat';
            } else {
                alert(data.error || 'Sign up failed');
            }
        } catch (error) {
            alert('An error occurred. Please try again.');
        }
    });
});
