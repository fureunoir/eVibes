import {createRouter, createWebHistory, RouterView} from 'vue-router'
import HomePage from "@/pages/home-page.vue";
import translation from "@/core/helpers/translations.js";
import {APP_NAME} from "@/config/index.js";

const routes = [
  {
    path: '/:locale?',
    component: RouterView,
    beforeEnter: translation.routeMiddleware,
    children: [
      {
        path: '',
        name: 'home',
        component: HomePage,
        meta: {
          title: "Home"
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    document.querySelector('#top').scrollIntoView({ behavior: 'smooth' })
    return {
      top: 0,
      left: 0,
      behavior: 'smooth'
    }
  }
})

router.beforeEach((to, from) => {
  document.title = to.meta.title ? `${APP_NAME} | ` + to.meta?.title : APP_NAME
})

export default router