import '../../src/frame/nhimc-frame.js';
import { initNhimcComponents } from '../../src/components/controllers.js';

const frame = document.querySelector('#app-frame');
const content = document.querySelector('#business-content');

const menu = [
  { id: 'access', label: 'Access', children: [
    { id: 'roles', label: 'Roles', href: '#roles' },
    { id: 'groups', label: 'Groups', href: '#groups' },
  ] },
  { id: 'governance', label: 'Governance', children: [
    { id: 'policies', label: 'Policies', href: '#policies' },
    { id: 'audit', label: 'Audit events', children: [{ id: 'exports', label: 'Exports', href: '#exports' }] },
  ] },
  { id: 'settings', label: 'Workspace settings', href: '#settings' },
];

const views = {
  access: ['Access administration', 'Fictional roles and policies for Northstar Services.'],
  roles: ['Role register', 'Assign fictional workspace capabilities by role.'],
  groups: ['Group directory', 'Organize fictional members without duplicating the frame.'],
  governance: ['Governance', 'Review policy coverage and audit readiness.'],
  policies: ['Policy library', 'Maintain fictional access and retention policies.'],
  audit: ['Audit events', 'Inspect synthetic workspace activity.'],
  exports: ['Audit exports', 'Prepare a fictional event export.'],
  settings: ['Workspace settings', 'Configure this fictional administration workspace.'],
};

function renderRoute(id) {
  const [title, description] = views[id] ?? views.access;
  content.querySelector('h1').textContent = title;
  content.querySelector('.nhimc-page-header p').textContent = description;
  content.dataset.route = id;
}

frame.menu = menu;
frame.activeId = 'access';
frame.addEventListener('nhimc:navigate', (event) => {
  frame.activeId = event.detail.id;
  renderRoute(event.detail.id);
});
initNhimcComponents(document);
