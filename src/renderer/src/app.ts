import { route } from '@aurelia/router'

@route({
    routes: [
        { path: '', redirectTo: 'startup' },
        { path: 'startup', component: () => import('./views/startup'), title: 'Starting Up' },
        { path: 'home', component: () => import('./views/home'), title: 'Home' },
        { path: 'workspace', component: () => import('./views/workspace'), title: 'Workspace' },
    ],
})
export class App {
}

