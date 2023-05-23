import { createRouter, createWebHistory } from "vue-router";
import HomePage from "@/views/HomePage.vue";
import NewQuizPage from "@/views/NewQuizPage.vue";
import QuestionManager from "@/views/QuestionManager.vue";
import ResultPage from "@/views/ResultPage.vue";
import Login from "@/components/admin/Login.vue";
import AdminQuestion from "@/components/admin/AdminQuestion.vue";
import AdminQuestionsList from "@/components/admin/AdminQuestionsList.vue";
import AdminNewQuestion from "@/components/admin/AdminNewQuestion.vue";
import AdminDelete from "@/components/admin/AdminDelete.vue";
import AdminEditQuestion from "@/components/admin/AdminEditQuestion.vue";
import authenticationService from "@/services/AuthenticationService";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomePage,
    },
    {
      path: "/start",
      name: "start",
      component: NewQuizPage,
    },
    {
      path: "/quiz",
      name: "quiz",
      component: QuestionManager,
    },
    {
      path: "/score",
      name: "score",
      component: ResultPage,
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../views/Admin.vue"),
      children: [
        {
          path: "login",
          name: "login",
          component: Login
        },
        {
          path: "question",
          name: "questions",
          component: AdminQuestionsList
        },
        {
          path: "question/:id",
          name: "question",
          component: AdminQuestion
        },
        {
          path: "question/:id/edit",
          name: "edit",
          component: AdminEditQuestion
        },
        {
          path: "question/new",
          name: "add",
          component: AdminNewQuestion
        },
        {
          path: "delete",
          name: "delete",
          component: AdminDelete
        }
      ],
      beforeEnter: to => {
        if (to.name !== "login" && !authenticationService.isLoggedIn())
          return { name: "login", query: { returnTo: to.fullPath } };
      }
    }
  ]
});

export default router;
