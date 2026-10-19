import ButtonGallery from './ButtonGallery.svelte';
import FormFieldExample from './FormFieldExample.svelte';
import AddRepositoryPreview from './AddRepositoryPreview.svelte';

export default { title: 'UI' };

export const Buttons = { render: () => ({ Component: ButtonGallery }) };
export const FormFields = { render: () => ({ Component: FormFieldExample }) };
export const AddRepositoryDialog = { render: () => ({ Component: AddRepositoryPreview }), parameters: { layout: 'fullscreen' } };
