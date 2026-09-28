import '../../src/frame/nhimc-frame.js';
import { initNhimcComponents } from '../../src/components/controllers.js';

const frame = document.querySelector('#app-frame');
const content = document.querySelector('#business-content');

const menu = [
  { id: 'overview', label: 'Overview', href: '#overview' },
  { id: 'queues', label: 'Queues', children: [{ id: 'priority', label: 'Priority queue', href: '#priority' }] },
  { id: 'tasks', label: 'Tasks', href: '#tasks' },
  { id: 'services', label: 'Service status', href: '#services' },
];

const views = {
  overview: ['Operations overview', 'Fictional work queues for Northstar Services.'],
  queues: ['Queue workspace', 'Compare waiting work by fictional service line.'],
  priority: ['Priority queue', 'Review the highest-impact fictional tasks first.'],
  tasks: ['Task register', 'Track ownership and completion without changing the shared frame.'],
  services: ['Service status', 'All fictional services are operating normally.'],
};

function renderRoute(id) {
  const [title, description] = views[id] ?? views.overview;
  content.querySelector('h1').textContent = title;
  content.querySelector('.nhimc-page-header p').textContent = description;
  content.dataset.route = id;
}

frame.menu = menu;
frame.activeId = 'overview';
frame.addEventListener('nhimc:navigate', (event) => {
  frame.activeId = event.detail.id;
  renderRoute(event.detail.id);
});
initNhimcComponents(document);
