document.addEventListener('DOMContentLoaded', () => {
    const input = document.querySelector('input[name="guests"]');
    const incBtn = document.querySelector('.increment');
    const decBtn = document.querySelector('.decrement');

    incBtn.addEventListener('click', () => {
        input.value = Math.min(parseInt(input.value) + 1, parseInt(input.max));
    });

    decBtn.addEventListener('click', () => {
        input.value = Math.max(parseInt(input.value) - 1, parseInt(input.min));
    });
});