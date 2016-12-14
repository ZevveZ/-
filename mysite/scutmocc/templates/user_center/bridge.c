#include <stdio.h>
#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
sem_t queue,east,west;
int et_num = 0,wt_num = 0;

void * eago(void*arg)
{
 int i =0; srand(int(time(0)));
 while(i<10){
 	sem_wait(&east);
 	 if(et_num == 0) sem_wait(&queue);
   int num =rand()%3+1;
 et_num += num;
 sem_post(&east);
 sleep(rand()%2+1);
 printf("%d east has through bridge!",num);
 sem_wait(&east);
 et_num -= num;
 if(et_num == 0)sem_post(queue);
 sem_post(&east);
 i++;
 }
 printf("eastgo end");
 }
void * wego(void*arg)
{
int n=0;srand(int(time(0)));
while(n<10){
	sem_wait(&west);
	 if(wt_num == 0){
     sem_wait(&queue);
  }
  int num =rand()%3+1;
 wt_num += num;
   sem_post(&west);
 sleep(rand()%2+1);
 printf(" %d west  has through bridge!",num);
 sem_wait(&west);
 wt_num -= num;
 if(wt_num == 0)sem_post(queue);
 sem_post(&west);
 n++;
}
 printf("westgo end");
 }
int main()
{
	pthread_t e1,e2,w1,w2;
	sem_init(&queue,0,1);
	pthread_create(&e1,NULL,eago,NULL);
	pthread_create(&e2,NULL,eago,NULL);
	pthread_create(&w2,NULL,eago,NULL);
	pthread_create(&w1,NULL,wego,NULL);

}