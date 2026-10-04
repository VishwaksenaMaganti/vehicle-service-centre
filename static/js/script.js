/**
 * Vehicle Service Centre Management System
 * Client-Side JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 2. Safe Delete Confirmation
    const deleteForms = document.querySelectorAll('form.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const itemType = form.getAttribute('data-item-type') || 'record';
            const itemName = form.getAttribute('data-item-name') || '';
            const msg = itemName 
                ? `Are you sure you want to delete ${itemType} "${itemName}"?\nThis action cannot be undone.`
                : `Are you sure you want to delete this ${itemType}?\nThis action cannot be undone.`;
            
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // 3. Form input validation helpers
    const positiveNumberInputs = document.querySelectorAll('input[type="number"][min="0"]');
    positiveNumberInputs.forEach(input => {
        input.addEventListener('input', () => {
            if (parseFloat(input.value) < 0) {
                input.value = 0;
            }
        });
    });
});
